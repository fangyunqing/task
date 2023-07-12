# @Time    : 2023/06/29 14:31
# @Author  : fyq
# @File    : toutiao.py
# @Software: PyCharm

__author__ = 'fyq'

import json
from typing import Optional

from aiohttp import ClientResponse

from core import constant
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.toutiao.util import util2

_PARAMS = "aid=24&account_sdk_source=sso&language=zh"


class IndexApi(AbstractApi):
    url = "https://sso.toutiao.com/"
    method = constant.hm.get
    api_types = ['toutiao']
    task_types = [constant.kw.login]

    async def _before(self, session):
        pass

    async def _after(self, response: ClientResponse, session) -> bool:
        pass


class SendActivationCodeApi(AbstractApi):
    url = "https://sso.toutiao.com/send_activation_code/v2/"
    method = constant.hm.get
    api_types = ['toutiao']
    task_types = [constant.kw.login]
    error_code = 0

    async def _before(self, session):
        self.url = _PARAMS
        self.data = util2.algorithm1(
            d1={
                "mobile": "+86 18750767178",
                "type": 24,
                "is6Digits": 1
            },
            d2=[
                "mobile",
                "type"
            ]
        )

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        self.error_code = text_json["error_code"]
        if self.error_code == 1105:
            verify_center_decision_conf: str = text_json["verify_center_decision_conf"]
            verify_center_decision_conf = verify_center_decision_conf.replace("\\", "")
            self.config.verify = json.loads(verify_center_decision_conf)
        return self.error_code == 0

    def fail(self) -> Optional[InvokeInfo]:
        pass



