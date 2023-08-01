# @Time    : 2023/07/21 10:14
# @Author  : fyq
# @File    : ask.py
# @Software: PyCharm

__author__ = 'fyq'

import json

import munch
from aiohttp import ClientResponse, ClientSession

from core import constant
from core.api.abstract_api import AbstractApi

import random

from core.api.baidu.util import util7


def _new_br():
    return {
        "a": random.randint(550, 565),
        "b": random.randint(520, 540),
        "c": 990,
        "d": 911,
        "m": "refreshAgin"
    }


class OrderListApi(AbstractApi):
    url = "https://wen.baidu.com/nchat/api/getorderlist"
    method = constant.hm.GET
    api_types = ['ask_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session: ClientSession):
        self.data = {
            "htj_to": util7.token(),
            "htj_vw": util7.view([ck.value for ck in session.cookie_jar if ck.key == "BAIDUID"][0]),
            "htj_jt": util7.jt(),
            "htj_app": "universe",
            "listtype": "payorder",
            "subsidyTokenVersion": "v1",
            "pn": 0,
            "rn": 20,
            "verifyCodeDs": "",
            "verifyCodeToken": "",
            "verifyInfo": util7.verify_info(),
            "hvi": util7.hvi(json.dumps(_new_br(), separators=(',', ':'))),
            "url": "/nchat/api/getorderlist"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERRNO] == 0:
            self.task.info(f"问一问:{text_json}")
            return True
        else:
            self.task.error(text_json[constant.error.ERRMSG])
            return False
