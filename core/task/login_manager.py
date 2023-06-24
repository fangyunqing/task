# @Time    : 2023/06/01 15:33
# @Author  : fyq
# @File    : login_manager.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import os
from json.decoder import JSONDecodeError
from typing import Type, Dict, Iterable, List, cast

import aiohttp
from aiohttp import ClientSession, TraceRequestStartParams, TraceRequestEndParams, ContentTypeError
from loguru import logger
from munch import Munch

from core.account import Account
from core.exception import ReLoginException
from core.task.abstract_task import LoginTask, logins_cls_list
from core.task.task import Task

import aiofiles


class LoginManager:

    def __init__(self, opt: Munch):
        self._logins: Dict[str, Type[LoginTask]] = {_.task_name: _ for _ in logins_cls_list}
        self._logger = logger
        self._opt = opt

    def create_trace_config(self) -> List[aiohttp.TraceConfig]:
        if self._opt.debug:
            tc = aiohttp.TraceConfig()
            tc.on_request_start.append(self._on_request_start)
            tc.on_request_end.append(self._on_request_end)
            return [tc]
        else:
            return []

    async def save_cookie(self, name: str, session: aiohttp.ClientSession):
        if isinstance(session.cookie_jar, aiohttp.CookieJar):
            cast(aiohttp.CookieJar, session.cookie_jar).save(f"{self._opt.cookies_path}{os.sep}{name}.cookies")

    async def load_cookie(self, name: str):
        cookie_jar = aiohttp.CookieJar()
        file_path = f"{self._opt.cookies_path}{os.sep}{name}.cookies"
        if os.path.isfile(file_path):
            cookie_jar.load(file_path)
        return cookie_jar

    async def login_before_exec(self, login_name: str, account: Account, task: Task):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=task.opt, account=account)
        cookie_jar = await self.load_cookie(login_name)
        async with aiohttp.ClientSession(headers=login_task.headers,
                                         trace_configs=self.create_trace_config(),
                                         connector=aiohttp.TCPConnector(ssl=False),
                                         cookie_jar=cookie_jar) as session:
            while True:
                await login_task.exec(session=session)
                await self.save_cookie(login_name, session)
                task.config.login = login_task.config.login
                try:
                    await task.exec(session=session)
                except ReLoginException:
                    pass

    def __getitem__(self, item) -> Type[LoginTask]:
        return self._logins.get(item)

    def __iter__(self) -> Iterable[Type[LoginTask]]:
        return iter(self._logins.values())

    async def run_login(self, login_name: str, account: Account):
        login_cls = self._logins.get(login_name)
        assert login_cls is not None
        login_task = login_cls(opt=self._opt, account=account)
        cookie_jar = await self.load_cookie(login_name)
        async with aiohttp.ClientSession(headers=login_task.headers,
                                         trace_configs=self.create_trace_config(),
                                         connector=aiohttp.TCPConnector(ssl=False),
                                         cookie_jar=cookie_jar) as session:
            await login_task.exec(session=session)
            await self.save_cookie(login_name, session)

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

        self._logger.debug("\n" + json.dumps(data, indent="   "))

    async def _on_request_end(self,
                              session: ClientSession,
                              tc: aiohttp.TraceConfig,
                              params: TraceRequestEndParams):
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
