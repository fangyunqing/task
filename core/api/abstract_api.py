# @Time    : 2023/06/01 11:16
# @Author  : fyq
# @File    : abstract_api.py
# @Software: PyCharm

__author__ = 'fyq'

from abc import abstractmethod
from typing import Optional, Union, List

from aiohttp import ClientSession, ClientResponse

from core.api import Api, InvokeInfo
from core.constant import hm
from core.exception import ApiException


class AbstractApi(Api):

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        pass

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        pass

    def fail(self) -> Optional[InvokeInfo]:
        return None

    def success(self) -> Optional[InvokeInfo]:
        return None

    @property
    def stop(self) -> bool:
        return False

    @abstractmethod
    async def _before(self, session):
        """
            前置处理
        :param session:
        :return:
        """
        pass

    @abstractmethod
    async def _after(self, response: ClientResponse, session) -> bool:
        """
            后置处理
            判断请求的成功或者失败
        :param session:
        :param response:
        :return:
        """

    async def request(self, session: ClientSession) -> bool:

        await self._before(session=session)

        if self.can_request:
            if self.method == hm.GET:
                response = await session.get(self.url, params=self.data, proxy=self.task.opt.proxy)
            elif self.method == hm.POST_DATA:
                response = await session.post(self.url, data=self.data, proxy=self.task.opt.proxy)
            elif self.method == hm.POST_JSON:
                response = await session.post(self.url, json=self.data, proxy=self.task.opt.proxy)
            elif self.method == hm.DELETE:
                response = await session.delete(self.url, proxy=self.task.opt.proxy)
            elif self.method == hm.HEAD:
                response = await session.head(self.url, proxy=self.task.opt.proxy)
            elif self.method == hm.OPTIONS:
                response = await session.options(self.url, proxy=self.task.opt.proxy)
            elif self.method == hm.PUT:
                response = await session.put(self.url, data=self.data, proxy=self.task.opt.proxy)
            else:
                if self.method:
                    raise ApiException(f"{self.api_sign}的方法{self.method}不支持")
                else:
                    raise ApiException(f"{self.api_sign}未设置方法")

            response.raise_for_status()
            res = await self._after(response, session)
            response.close()
            if res:
                self.task.info(f"{self.api_name} is success")
            else:
                self.task.info(f"{self.api_name} is fail")
            return res
        else:
            return True


class AbstractNodeApi(AbstractApi):

    async def _before(self, session):
        self.can_request = False
        await self._ready_data()

    async def _after(self, response: ClientResponse, session) -> bool:
        pass

    def success(self) -> Optional[InvokeInfo]:
        return self._next()

    @abstractmethod
    async def _ready_data(self):
        pass

    @abstractmethod
    def _next(self):
        pass
