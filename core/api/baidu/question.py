# @Time    : 2023/06/16 13:31
# @Author  : fyq
# @File    : question.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import random
from typing import Optional

from aiohttp import ClientResponse

from core import constant, chatgpt
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import utdata
from core.util.time import thirteen_digits_time


class ChoiceApi(AbstractApi):
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    api_names = [
        # "homepage",
        "getqlist319"
    ]
    active_api = None

    async def _before(self):
        self.can_request = False
        self.active_api = random.choice(self.api_names)

    async def _after(self, response: ClientResponse) -> bool:
        pass

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo(self.active_api)


class GetQList319(AbstractApi):
    url = "https://zhidao.baidu.com/activity/ajax/getqlist"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        self.data = {
            "packageId": 319
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            question_list = text_json["data"]["list"]
            q_len = len(question_list)
            if q_len > 0:
                question = question_list[random.randint(0, q_len - 1)]
                self.config.question = f"{question['qTitle']},有哪些典故,有哪些农事,有哪些寓意,有哪些案例"
                self.config.qid = question["encodeQid"]
                self.config.entry = "iknowduck_92"
                return True
            else:
                return False
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("submitajax")


class HomePageApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/homepage"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        self.data = {
            "pn": 20 * random.randint(0, 10),
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
            q_len = len(question_list)
            if q_len > 0:
                question = question_list[random.randint(0, q_len - 1)]
                # 不回答图片的问题
                if question.setdefault("contentRich", None):
                    return False
                content: str = question['content'].strip()
                title: str = question['title'].strip()
                if content or title:
                    self.config.question = f"{title}.{content}"
                    self.config.entry = "list_highScore_all"
                    self.config.qid = question["qid"]
                    return True
                else:
                    return False
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

    async def _before(self):
        try:
            question = self.config.question
            if len(question) < 5:
                self.can_request = False
                return

            answer = await chatgpt.invoke_3d5_turbo(question)
            self.task.info(f"\nq:[{question}]\na:[{answer.a}]\nsa:[{answer.sa}]")
            if answer is None or len(answer.a) < 10:
                self.can_request = False
                return

            self.data = {
                "cm": 100009,
                "qid": self.config.qid,
                "title": "",
                "answerfr": "",
                "feedback": 0,
                "entry": self.config.entry,
                "co": f"<p>{answer.a}<p>",
                "cite": "",
                "rich": 1,
                "edit": "new",
                "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
                "stoken": self.config.login["stoken"]
            }
        except Exception as e:
            self.task.error(str(e))

    async def _after(self, response: ClientResponse) -> bool:
        return True
