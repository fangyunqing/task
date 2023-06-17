# @Time    : 2023/05/31 9:03
# @Author  : fyq
# @File    : task.py
# @Software: PyCharm

from __future__ import annotations

__author__ = 'fyq'

from abc import ABC, abstractmethod
from typing import Optional

import loguru
from aiohttp import ClientSession
from munch import Munch


class Task(ABC):
    """
        所有任务的基类
    """

    # 任务的配置项
    # 提供给接口使用
    # 接口返回的数据
    config: Munch = None

    def __init__(self, opt: Optional[Munch]):
        self.opt = opt
        self._logger = loguru.logger

    @abstractmethod
    async def exec(self, session: ClientSession):
        pass

    @abstractmethod
    def task_sign(self):
        pass

    def debug(self, message: str):
        if self.opt.debug:
            self._logger.debug(f"{self.task_sign} - {message}")

    def info(self, message: str):
        self._logger.info(f"{self.task_sign} - {message}")

    def error(self, message: str):
        self._logger.error(f"{self.task_sign} - {message}")

    def warning(self, message: str):
        self._logger.warning(f"{self.task_sign} - {message}")


