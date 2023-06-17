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

    def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        pass

    def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        pass

    def fail(self) -> Optional[InvokeInfo]:
        return None

    def success(self) -> Optional[InvokeInfo]:
        return None

    @property
    def stop(self) -> bool:
        return False

    @abstractmethod
    def _before(self):
        """
            前置处理
        :return:
        """
        pass

    @abstractmethod
    async def _after(self, response: ClientResponse) -> bool:
        """
            后置处理
            判断请求的成功或者失败
        :param response:
        :return:
        """

    async def request(self, session: ClientSession) -> bool:

        self._before()

        if self.method == hm.get:
            response = await session.get(self.url, params=self.data, proxy=self.task.opt.proxy)
        elif self.method == hm.post_data:
            response = await session.post(self.url, data=self.data, proxy=self.task.opt.proxy)
        elif self.method == hm.post_json:
            response = await session.post(self.url, json=self.data, proxy=self.task.opt.proxy)
        elif self.method == hm.delete:
            response = await session.delete(self.url, proxy=self.task.opt.proxy)
        elif self.method == hm.head:
            response = await session.head(self.url, proxy=self.task.opt.proxy)
        elif self.method == hm.options:
            response = await session.options(self.url, proxy=self.task.opt.proxy)
        elif self.method == hm.put:
            response = await session.put(self.url, data=self.data, proxy=self.task.opt.proxy)
        else:
            if self.method:
                raise ApiException(f"{self.api_sign}的方法{self.method}不支持")
            else:
                raise ApiException(f"{self.api_sign}未设置方法")

        response.raise_for_status()
        res = await self._after(response)
        response.close()
        return res

