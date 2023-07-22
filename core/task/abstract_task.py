# @Time    : 2023/06/01 14:04
# @Author  : fyq
# @File    : abstract_task.py
# @Software: PyCharm

from __future__ import annotations

__author__ = 'fyq'

import asyncio
import datetime
from typing import Type, Dict, Any, List, Optional

import loguru
from aiohttp import ClientSession
from munch import Munch

from core import constant
from core.account import Account
from core.api import Api, InvokeInfo
from core.exception import TaskException, ReLoginException
from core.task.task import Task
from core.util.user_agent import random_ua

logins_cls_list: List[Type[LoginTask]] = []
schedule_cls_list: List[Type[ScheduleTask]] = []


class AbstractTask(Task):
    """
        抽象任务类
        定义执行方法和日志
        任务分为登录和定时器
        登录获取凭证
        定时器定时执行任务
    """

    # 任务所需接口 api_name:api_cls
    # 验证接口的链路
    apis: Dict[str, Type[Api]]

    # 任务开始的接口名称
    first_api_name: str

    # 任务的类型 登录 定时器
    task_type: str

    # 接口类型
    # 按顺序获取接口
    # 同名的情况下 后者覆盖前者
    api_types: List[str] = None

    # 任务名称
    task_name: str = ""

    def __init__(self, opt: Optional[Munch]):
        super(AbstractTask, self).__init__(opt=opt)
        self._logger = loguru.logger

    def __repr__(self):
        return f"{self.task_sign} api_types:{self.api_types}"

    def __new__(cls, *args, **kwargs):
        assert cls is not AbstractTask
        return super().__new__(cls)

    async def exec(self, session: ClientSession):

        self.config.user_agent = session.headers.get("User-Agent")

        api_name = self.first_api_name
        assert api_name is not None
        next_invoker_info = InvokeInfo(api_name=api_name)
        while True:
            if next_invoker_info:
                next_api_cls: Type[Api] = self.apis.get(next_invoker_info.api_name)
                if next_api_cls is None:
                    raise TaskException(f"{self.task_sign}接口{next_invoker_info.api_name}未找到")
            else:
                raise TaskException(f"{self.task_sign}未找到下一个接口")
            current_api = next_api_cls(task=self, config=self.config, invoke_config=next_invoker_info.config)
            if pre_invoke_infos := await current_api.pre():
                if isinstance(pre_invoke_infos, List):
                    for pre_invoke_info in pre_invoke_infos:
                        pre_api_cls: Type[Api] = self.apis.get(pre_invoke_info.api_name)
                        if pre_api_cls:
                            await asyncio.sleep(self.opt.sleep_time)
                            await pre_api_cls(task=self,
                                              config=self.config,
                                              invoke_config=pre_invoke_info.config).request(session=session)
                        else:
                            self.warning(f"{pre_invoke_info.api_name}未注册")
                else:
                    pre_api_cls: Type[Api] = self.apis.get(pre_invoke_infos.api_name)
                    if pre_api_cls:
                        await asyncio.sleep(self.opt.sleep_time)
                        await pre_api_cls(task=self,
                                          config=self.config,
                                          invoke_config=pre_invoke_infos.config).request(session=session)
                    else:
                        self.warning(f"{pre_invoke_infos.api_name}未注册")
            await asyncio.sleep(self.opt.sleep_time)
            res = await (current_api.request(session=session))
            if not res:
                next_invoker_info = current_api.fail()
                if next_invoker_info is None:
                    break
            else:
                if post_invoke_infos := await current_api.post():
                    if isinstance(post_invoke_infos, List):
                        for post_invoke_info in post_invoke_infos:
                            post_api_cls: Type[Api] = self.apis.get(post_invoke_info.api_name)
                            if post_api_cls:
                                await asyncio.sleep(self.opt.sleep_time)
                                await post_api_cls(task=self,
                                                   config=self.config,
                                                   invoke_config=post_invoke_info.config).request(session=session)
                            else:
                                self.warning(f"{post_invoke_info.api_name}未注册")
                    else:
                        post_api_cls: Type[Api] = self.apis.get(post_invoke_infos.api_name)
                        if post_api_cls:
                            await asyncio.sleep(self.opt.sleep_time)
                            await post_api_cls(task=self,
                                               config=self.config,
                                               invoke_config=post_invoke_infos.config).request(session=session)
                        else:
                            self.warning(f"{post_invoke_infos.api_name}未注册")

                if current_api.stop or current_api.success() is None:
                    break
                next_invoker_info = current_api.success()

    @property
    def task_sign(self):
        return f"{self.task_type}-{self.task_name}"


class ScheduleTask(AbstractTask):
    """
        定时任务
        一般具有先执行登录
        并且会定时执行
    """

    # 登录task名称
    login_name: str

    # 重复时间 单位秒
    repeat_time: int = 120

    # 任务开始 小时
    start_hour: int = None

    # 任务不执行时间段 小时
    non_execution: List[int] = None

    def __init__(self, opt: Optional[Munch]):
        super(ScheduleTask, self).__init__(opt)

    def __new__(cls, *args, **kwargs):
        assert cls is not ScheduleTask
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        cls.task_type = constant.kw.SCHEDULE
        cls.task_name = cls.__name__.replace(cls.task_type.title(), "").lower()
        schedule_cls_list.append(cls)

    async def exec(self, session: ClientSession):
        while True:
            try:
                if self.start_hour:
                    while True:
                        if datetime.datetime.now().hour < self.start_hour:
                            await asyncio.sleep(1800)
                        else:
                            break

                if self.non_execution:
                    while True:
                        if datetime.datetime.now().hour in self.non_execution:
                            await asyncio.sleep(1800)
                        else:
                            break

                await super().exec(session=session)
            except ReLoginException as re:
                raise re
            except Exception as e:
                self.exception(str(e))
            finally:
                await asyncio.sleep(self.repeat_time)


class LoginTask(AbstractTask):
    """
    登录任务
    """

    # 来源
    referer = ""

    # 登录账户
    account: Account = None

    def __init__(self, opt: Optional[Munch], account: Account):
        super(LoginTask, self).__init__(opt=opt)
        self.account = account
        self.config.account = account

    def __new__(cls, *args, **kwargs):
        assert cls is not LoginTask
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        cls.task_type = constant.kw.LOGIN
        cls.task_name = cls.__name__.replace(cls.task_type.title(), "").lower()
        logins_cls_list.append(cls)

    @property
    def headers(self) -> Dict[str, Any]:
        headers = {
            constant.kw.UA: random_ua()
        }

        if self.referer:
            headers["Referer"] = self.referer

        return headers


class CombinationTask(Task):
    """
        组合任务
        一般多个schedule任务 具有同一个登录
    """

    def task_sign(self):
        return f"combination: {self.login_name}"

    def __init__(self, login_name: str, st_cls_list: List[Type[ScheduleTask]], opt: Optional[Munch]):
        super(CombinationTask, self).__init__(opt)
        self._st_cls_list = st_cls_list
        self.login_name = login_name
        self.config = Munch()

    def __repr__(self):
        return f"{self.login_name}-{[_.task_sign for _ in self._st_cls_list]}"

    async def exec(self, session: ClientSession):
        tasks = [task_cls(self.opt) for task_cls in self._st_cls_list]
        wait_tasks = []
        for task in tasks:
            task.config.login = self.config.login
            wait_tasks.append(task.exec(session))
        await asyncio.wait(wait_tasks)

