# @Time    : 2023/05/30 14:55
# @Author  : fyq
# @File    : interface.py
# @Software: PyCharm

from __future__ import annotations

__author__ = 'fyq'

from abc import abstractmethod, ABC
from typing import Union, List, TYPE_CHECKING, Optional, Tuple, Dict, Type

from aiohttp import ClientSession
from munch import Munch

from core import constant

if TYPE_CHECKING:
    from core.task import Task

api_cls_list: List[Type[Api]] = []


class Api(ABC):
    """
        所有接口的基类
        定义一个接口用于发起请求
        发起请求之前 外部调用 pre
        然后外部调用 request 发送一个执行
        如果请求被认为失败了 外部调用 request_if_fail
        如果请求被认为成功了 外部调用 stop and next
    """

    # 接口地址 eg: https://passport.baidu.com/v2/getpublickey
    # 接口不需要带参数
    # 参数会在data中以字典的形式定义
    url: str

    # http请求的方式 get post_data post_json put delete...
    # 一些方式中参数无效 无法传递
    method: str

    # 需求传递的参数
    # post get
    data: dict

    # 任务类型
    # login 登录
    # schedule 定时
    task_types: List[str]

    # 接口类型
    # 指示接口用于具体的哪种类型
    # 比如接口用于baidu登录中一个环节 像获取验证图片 验证码
    api_types: List[str]

    # 接口名称
    api_name: str

    # 任务实例
    # 调用此接口的任务
    task: "Task" = None

    def __init__(self, task: "Task", config: Munch):
        self.task = task
        self.config = config

    def __repr__(self):
        return f"{self.api_sign}:{self.method} {self.url}"

    def __init_subclass__(cls, **kwargs):
        cls.api_name = cls.__name__.replace(constant.kw.api.title(), "", __count=1).lower()
        if constant.kw.abstract.lower() not in cls.api_name:
            api_cls_list.append(cls)

    @abstractmethod
    def pre(self) -> Optional[str]:
        pass

    @abstractmethod
    async def request(self, session: ClientSession) -> Tuple[bool, Optional[Dict]]:
        pass

    @property
    def api_sign(self):
        return f"{self.task_types}-{self.api_types}-{self.api_name}"

    @abstractmethod
    def request_if_fail(self) -> Optional[str]:
        pass

    @abstractmethod
    def next(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def stop(self) -> bool:
        pass



