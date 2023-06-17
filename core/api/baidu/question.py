# @Time    : 2023/06/16 13:31
# @Author  : fyq
# @File    : question.py
# @Software: PyCharm

__author__ = 'fyq'

import asyncio
import json
import random
from typing import Optional, List

from aiohttp import ClientResponse, ClientSession

from core import constant
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import utdata
from core.util.time import thirteen_digits_time


class HomePageApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/homepage"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    def _before(self):
        self.data = {
            "pn": 0,
            "rn": 20,
            "ie": "utf8",
            "type": "highScore",
            "tag": "",
            "cid": "",
            "keyWord": "",
            "category": "",
            "t": thirteen_digits_time()
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            question_list = text_json["data"]["list"]
            if q_len := len(question_list) > 0:
                self.config.question = question_list[random.randint(0, q_len - 1)]
                return True
            else:
                return False
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("submitajax")


class SubmitAjaxApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    def _before(self):
        self.data = {
                "cm": 100009,
                "qid": self.config.question["qid"],
                "title": "",
                "answerfr": "",
                "feedback": 0,
                "entry": "list_highScore_all",
                "co": f"<p>{self.config.question['title']}<p>",
                "cite": "",
                "rich": 1,
                "edit": "new",
                "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
                "stoken": self.config.login["stoken"]
            }

    async def _after(self, response: ClientResponse) -> bool:
        return True

