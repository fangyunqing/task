# @Time    : 2023/06/01 11:16
# @Author  : fyq
# @File    : abstract_api.py
# @Software: PyCharm

__author__ = 'fyq'

from abc import abstractmethod
from typing import Tuple, Optional, Dict

from aiohttp import ClientSession, ClientResponse

from core.api import Api
from core.constant import hm
from core.exception import ApiException


class AbstractApi(Api):

    def pre(self) -> Optional[str]:
        return None

    def request_if_fail(self) -> Optional[str]:
        return None

    def next(self) -> Optional[str]:
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
    async def _after(self, response: ClientResponse) -> Tuple[bool, Optional[Dict]]:
        """
            后置处理
            判断请求的成功或者失败
        :param response:
        :return:
        """
        pass

    async def request(self, session: ClientSession) -> Tuple[bool, Optional[Dict]]:

        self._before()

        if self.method == hm.get:
            response = await session.get(self.url, params=self.data, proxy="http://127.0.0.1:8888")
        elif self.method == hm.post_data:
            response = await session.post(self.url, data=self.data)
        elif self.method == hm.post_json:
            response = await session.post(self.url, json=self.data)
        elif self.method == hm.delete:
            response = await session.delete(self.url)
        elif self.method == hm.head:
            response = await session.head(self.url)
        elif self.method == hm.options:
            response = await session.options(self.url)
        elif self.method == hm.put:
            response = await session.put(self.url, data=self.data)
        else:
            if self.method:
                raise ApiException(f"{self.api_sign}的方法{self.method}不支持")
            else:
                raise ApiException(f"{self.api_sign}未设置方法")
        res = await self._after(response)
        response.close()
        return res

