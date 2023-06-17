# @Time    : 2023/06/01 15:33
# @Author  : fyq
# @File    : login_manager.py
# @Software: PyCharm

__author__ = 'fyq'

import json
from json.decoder import JSONDecodeError
from typing import Type, Dict, Iterable

import aiohttp
from aiohttp import ClientSession, TraceRequestStartParams, TraceRequestEndParams, ContentTypeError
from loguru import logger
from munch import Munch

from core.account import Account
from core.task.abstract_task import LoginTask, logins_cls_list
from core.task.task import Task


class LoginManager:

    def __init__(self, opt: Munch):
        self._logins: Dict[str, Type[LoginTask]] = {_.task_name: _ for _ in logins_cls_list}
        self._logger = logger
        self._opt = opt

    async def login_before_exec(self, login_name: str, account: Account, task: Task):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=task.opt, account=account)
        tc = aiohttp.TraceConfig()
        tc.on_request_start.append(self._on_request_start)
        tc.on_request_end.append(self._on_request_end)
        async with aiohttp.ClientSession(headers=login_task.headers,
                                         trace_configs=[tc],
                                         connector=aiohttp.TCPConnector(ssl=False)) as session:
            await login_task.exec(session=session)
            task.config.login = login_task.config.login
            await task.exec(session=session)

    def __getitem__(self, item) -> Type[LoginTask]:
        return self._logins.get(item)

    def __iter__(self) -> Iterable[Type[LoginTask]]:
        return iter(self._logins.values())

    async def run_login(self, login_name: str, account: Account):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=self._opt, account=account)
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
        if self._opt.debug:
            data = {
                "url": str(params.url),
                "method": params.method,
                "headers": {k: v for k, v in params.headers.items()},
                "cookies": {cj.key: cj for cj in session.cookie_jar}
            }

            self._logger.debug("\n" + json.dumps(data, indent="   "))

    async def _on_request_end(self,
                              session: ClientSession,
                              tc: aiohttp.TraceConfig,
                              params: TraceRequestEndParams):
        if self._opt.debug:
            try:
                json_text = await params.response.json()
            except (ContentTypeError, JSONDecodeError):
                json_text = "..."

            try:
                text = await params.response.text()
            except UnicodeDecodeError:
                text = "..."

            if len(text) > self._opt.response_len:
                text = "..."

            response = {
                "status": params.response.status,
                "json": json_text,
                "text": text,
                "cookies": params.response.cookies
            }
            data = {
                "url": str(params.url),
                "method": params.method,
                "headers": {k: v for k, v in params.headers.items()},
                "response": response
            }
            self._logger.debug("\n" + json.dumps(data, indent="   "))
