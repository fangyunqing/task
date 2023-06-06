# @Time    : 2023/06/01 15:33
# @Author  : fyq
# @File    : login_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from json.decoder import JSONDecodeError
from types import SimpleNamespace
from typing import Type, Dict, Iterable

import aiohttp
import simplejson
from aiohttp import ClientSession, TraceRequestStartParams, ClientResponse, TraceRequestEndParams, ContentTypeError
from loguru import logger
from munch import Munch
from yarl import URL

from core.task.abstract_task import LoginTask, logins_cls_list
from core.task.task import Task


class LoginManager:

    def __init__(self):
        self._logins: Dict[str, Type[LoginTask]] = {_.task_name: _ for _ in logins_cls_list}
        self._logger = logger

    async def login_before_exec(self, login_name: str, task: Task):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=task.opt)
        session = ClientSession(headers=login_task.headers)
        await login_task.exec(session=session)
        await task.exec(session=session)

    def __getitem__(self, item) -> Type[LoginTask]:
        return self._logins.get(item)

    def __iter__(self) -> Iterable[Type[LoginTask]]:
        return iter(self._logins.values())

    async def run_login(self, login_name: str, opt: Munch):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=opt)
        tc = aiohttp.TraceConfig()
        tc.on_request_start.append(self._on_request_start)
        tc.on_request_end.append(self._on_request_end)
        async with aiohttp.ClientSession(headers=login_task.headers,
                                         trace_configs=[tc],
                                         connector=aiohttp.TCPConnector(ssl=False)) as session:
            await login_task.exec(session=session)

    async def _on_request_start(self,
                                session: ClientSession,
                                tc: aiohttp.TraceConfig,
                                params: TraceRequestStartParams):
        data = {
            "url": str(params.url),
            "method": params.method,
            "headers": {k: v for k, v in params.headers.items()},
            "cookies": {cj.key: cj for cj in session.cookie_jar}
        }
        self._logger.debug("\n" + simplejson.dumps(data, indent="   "))

    async def _on_request_end(self,
                              session: ClientSession,
                              tc: aiohttp.TraceConfig,
                              params: TraceRequestEndParams):
        try:
            json = await params.response.json()
        except (ContentTypeError, JSONDecodeError):
            json = "..."

        text = await params.response.text()
        if len(text) > 1024:
            text = "..."

        response = {
            "status": params.response.status,
            "json": json,
            "text": text,
            "cookies": params.response.cookies
        }
        data = {
            "url": str(params.url),
            "method": params.method,
            "headers": {k: v for k, v in params.headers.items()},
            "response": response
        }
        self._logger.debug("\n" + simplejson.dumps(data, indent="   "))
