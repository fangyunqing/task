# @Time    : 2023/06/01 15:33
# @Author  : fyq
# @File    : login_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Type, Dict, Iterable

from aiohttp import ClientSession

from core.task.abstract_task import LoginTask, logins_cls_list
from core.task.task import Task


class LoginManager:

    def __init__(self):
        self._logins: Dict[str, Type[LoginTask]] = {_.task_name: _ for _ in logins_cls_list}

    async def login_before_exec(self, login_name: str, session: ClientSession, task: Task):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=task.opt)
        await login_task.exec(session=session)
        await task.exec(session=session)

    def __getitem__(self, item) -> Type[LoginTask]:
        return self._logins.get(item)

    def __iter__(self) -> Iterable[Type[LoginTask]]:
        return iter(self._logins.values())