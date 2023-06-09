# @Time    : 2023/06/01 17:08
# @Author  : fyq
# @File    : application.py
# @Software: PyCharm

__author__ = 'fyq'

import asyncio
import aiohttp
from loguru import logger

from munch import Munch

from core.account import AccountManager
from core.api import ApiManager
from core.modules import modules
from core.task import LoginManager, ScheduleManager
import importlib

from core.task.abstract_task import CombinationTask
from core.settings import default_opt


class Application:

    def __init__(self):

        for module in modules:
            try:
                importlib.import_module(module)
            except (ValueError, KeyError, ModuleNotFoundError):
                logger.warning(f"模块 {module} 不存在")

        self.opt: Munch = Munch()
        self.opt.update(default_opt)

        self.am = ApiManager(self.opt)
        self.lm = LoginManager(self.opt)
        self.sm = ScheduleManager(self.opt)
        self.um = AccountManager(self.opt)
        self.opt: Munch = Munch({
            "debug": True,
            "proxy": False
        })

        for login_cls in self.lm:
            login_cls.apis = {}
            for api_type in login_cls.api_types:
                login_cls.apis.update(self.am.get_apis(login_cls.task_type, api_type))

    def run(self):
        wait_task_list = []
        for _ in self.sm.tasks:
            if isinstance(_, CombinationTask):
                task = _
                _.opt = self.opt
            else:
                task = _(opt=self.opt)
            wait_task_list.append(self.lm.login_before_exec(login_name=task.login_name,
                                                            task=task))
        if wait_task_list:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(fs=wait_task_list))

    def run_login(self, login_name: str):
        loop = asyncio.get_event_loop()
        for account in self.um.get_account(login_name):
            loop.run_until_complete(self.lm.run_login(login_name=login_name,
                                                      account=account))


app = Application()
