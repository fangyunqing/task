# @Time    : 2023/06/01 14:04
# @Author  : fyq
# @File    : abstract_task.py
# @Software: PyCharm

from __future__ import annotations

__author__ = 'fyq'

import asyncio
from typing import Type, Dict, Any, List, Optional

import loguru
from aiohttp import ClientSession
from munch import Munch

from core import constant
from core.task.task import Task
from core.api import Api
from core.exception import TaskException
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

    # 任务的配置项
    # 提供给接口使用
    # 接口返回的数据
    config: Munch = None

    # 任务的类型 登录 定时器
    task_type: str

    # 接口类型
    # 按顺序获取接口
    # 同名的情况下 后者覆盖前者
    api_types: List[str] = None

    # 任务名称
    task_name: str = ""

    # 会话
    session: ClientSession = None

    def __init__(self, opt: Optional[Munch]):
        super(AbstractTask, self).__init__(opt=opt)
        self._logger = loguru.logger

    def __repr__(self):
        return f"{self.task_sign} api_types:{self.api_types}"

    def __new__(cls, *args, **kwargs):
        assert cls is not AbstractTask
        return super().__new__(cls)

    async def exec(self, session: ClientSession):
        next_api_name = self.first_api_name
        assert next_api_name is not None
        while True:
            if next_api_name:
                next_api_cls: Type[Api] = self.apis.get(next_api_name)
                if next_api_cls is None:
                    raise TaskException(f"{self.task_sign}接口{next_api_name}未找到")
            else:
                raise TaskException(f"{self.task_sign}未找到下一个接口")
            current_api = next_api_cls(task=self, config=self.config)
            if pre_api_name := current_api.pre():
                pre_api_cls: Type[Api] = self.apis.get(pre_api_name)
                if pre_api_cls:
                    await pre_api_cls(task=self, config=self.config).request(session=session)
            await current_api.request(session=session)
            if current_api.stop or current_api.next() is None:
                break
            next_api_name = current_api.next()

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

    # 重复时间
    # 单位秒
    repeat_time: int = 60

    def __init__(self, opt: Optional[Munch]):
        super(ScheduleTask, self).__init__(opt)

    def __new__(cls, *args, **kwargs):
        assert cls is not ScheduleTask
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        schedule_cls_list.append(cls)

    async def exec(self, session: ClientSession):
        while True:
            await super().exec(session=session)
            await asyncio.sleep(self.repeat_time)


class LoginTask(AbstractTask):
    """
    登录任务
    """

    # header host
    host = ""

    # 来源
    referer = ""

    def __new__(cls, *args, **kwargs):
        assert cls is not LoginTask
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        cls.task_type = constant.kw.login
        cls.task_name = cls.__name__.replace(cls.task_type.title(), "").lower()
        logins_cls_list.append(cls)

    @property
    def headers(self) -> Dict[str, Any]:
        headers = {
            "User-Agent": random_ua()
        }
        if self.host:
            headers["Host"] = self.host
        if self.referer:
            headers["Referer"] = self.referer
        headers["Accept-Encoding"] = "identity"
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

    def __repr__(self):
        return f"{self.login_name}-{[_.task_sign for _ in self._st_cls_list]}"

    async def exec(self):
        await asyncio.wait([_(self.opt).exec() for _ in self._st_cls_list])