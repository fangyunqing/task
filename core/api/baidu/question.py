# @Time    : 2023/06/16 13:31
# @Author  : fyq
# @File    : question.py
# @Software: PyCharm

__author__ = 'fyq'

import glob
import json
import os
import random
import time
import uuid
from typing import Optional, List, Union
from urllib import parse

import aiohttp
import pyparsing as pp
from aiohttp import ClientResponse
from munch import Munch

from core import constant, chatgpt
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import utdata
from core.util.time import thirteen_digits_time

_IMAGE_SOURCE = "https://source.unsplash.com/960x640/?"

_QUESTION_PATTERN = ("你是一个资深的答主,"
                     "帮我回答关于「{}」的问题,要求答案包含相关图片,字数在500到1000之间,图片要尽量和答案匹配,"
                     "显示图片请用markdown语法 (" + _IMAGE_SOURCE + "<关键词>)")
_IMAGE_PATTERN = '<p><img src="{}" data_time="{}"/></p>'


class ChoiceApi(AbstractApi):
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    api_names = [
        "homepage",
        "getqlist319"
    ]
    active_api = None

    async def _before(self):
        self.can_request = False
        self.active_api = random.choice(self.api_names)
        for file in glob.glob(f"{self.task.opt.image_path}{os.sep}answer{os.sep}*"):
            os.remove(file)

    async def _after(self, response: ClientResponse) -> bool:
        pass

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo(self.active_api)


class GetQList319Api(AbstractApi):
    url = "https://zhidao.baidu.com/activity/ajax/getqlist"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    ASK_PATTERN = "[{}]问题是否询问习俗还是节日?节日回复1,风俗回复2,都是不是回复3"
    HOLIDAY_PATTERN = "{},节日由来,相关典故,寓意,庆祝方式以及相关扩展"
    CUSTOM_PATTERN = "{},习俗的详细介绍/来源解释,列举相关习俗案例以及相关扩展"

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

                ask_answer = await chatgpt.invoke_3d5_turbo(self.ASK_PATTERN.format(question['qTitle']))
                if ask_answer is None or ask_answer.a == "3":
                    self.config.question = _QUESTION_PATTERN.format(f"{question['qTitle']}")
                elif ask_answer.a == "2":
                    self.config.question = _QUESTION_PATTERN.format(self.CUSTOM_PATTERN.format(f"{question['qTitle']}"))
                else:
                    self.config.question = _QUESTION_PATTERN.format(
                        self.HOLIDAY_PATTERN.format(f"{question['qTitle']}")
                    )

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
    tags = ["动漫", "电视剧", "单机游戏"]

    async def _before(self):
        self.data = {
            "pn": 20 * random.randint(0, 10),
            "rn": 20,
            "ie": "utf8",
            "type": "highScore",
            "tag": random.choice(self.tags),
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
                    self.config.question = _QUESTION_PATTERN.format(f"{title}.{content}")
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

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if len(self.config.question) > 5:
            answer = await chatgpt.invoke_3d5_turbo(self.config.question)
            if answer is None or len(answer.a) < 10:
                self.can_request = False
                return
            self.task.info(f"\nq:[{self.config.question}]\na:[{answer.a}]\nsa:[{answer.sa}]")
            tag = pp.OneOrMore(pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + "'.,+-*!#$%&"))
            pp_url = pp.Literal("(") + pp.Literal("https://source.unsplash.com/960x640/?") + tag + pp.Literal(")")
            answers = []
            urls = []
            idx = 0
            for ps_idx, (u, s, e) in enumerate(pp_url.scan_string(answer.a)):
                urls.append("".join(u)[1:-1])
                sub: str = answer.a[idx:s]
                sub_idx = sub.index("![")
                if sub_idx > 0:
                    sub = sub[0: sub_idx]
                if sub:
                    answers.append(sub)
                answers.append(f"url{ps_idx}")
                idx = e
            answers.append(answer.a[idx:])
            if urls:
                self.config.answer = answers
            else:
                self.config.answer = answer.a

            return [InvokeInfo("uploadimage", Munch({"url": url, "tag": f"url{url_idx}"}))
                    for url_idx, url in enumerate(urls)]

    async def _before(self):
        if self.can_request:
            try:
                if isinstance(self.config.answer, List):
                    self.config.answer = "".join([a for a in self.config.answer if not a.startswith("url")])
                if _IMAGE_SOURCE in self.config.answer:
                    self.can_request = False
                    return
                self.data = {
                    "cm": 100009,
                    "qid": self.config.qid,
                    "title": "",
                    "answerfr": "",
                    "feedback": 0,
                    "entry": self.config.entry,
                    "co": f"<p>{self.config.answer}<p>",
                    "cite": "",
                    "rich": 1,
                    "edit": "new",
                    "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
                    "stoken": self.config.login["stoken"]
                }
            except Exception as e:
                self.task.exception(str(e))

    async def _after(self, response: ClientResponse) -> bool:
        return True

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("myanswer")


class MyAnswerApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/myanswer"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        self.data = {
            "pn": 0,
            "rn": 20,
            "t": thirteen_digits_time(),
            "type": "default"
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            questions = text_json["data"]["question"]["list"]
            for question in questions:
                if (
                        question["isDeleted"] == 1
                        and not question["appeal_time_exist"]
                        and question["deleted_by_self"] == 0
                        and question["isReview"] == 0
                ):
                    self.config.appeal = {
                        "qid": question["qid"],
                        "aid": question["replyId"]
                    }
                    return True
            return False
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("appeal")


class AppealApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        self.data = {
            "cm": 100043,
            "qid": self.config.appeal["qid"],
            "type": 100009,
            "aid": self.config.appeal["aid"],
            "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
            "stoken": self.config.login["stoken"]
        }

    async def _after(self, response: ClientResponse) -> bool:
        pass


class UploadImageApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.invoke_config.url) as response:
                    if response.status == 200:
                        image_path = f"{self.task.opt.image_path}{os.sep}answer"
                        if not os.path.exists(image_path):
                            os.makedirs(image_path)
                        image_name = f"{uuid.uuid4()}.jpg"
                        answer_image_path = f"{image_path}{os.sep}{image_name}"
                        with open(answer_image_path, 'wb') as fp:
                            fp.write(await response.read())
                        self.data: aiohttp.FormData = aiohttp.FormData()
                        self.data.add_field(name="image",
                                            value=open(answer_image_path, "rb"),
                                            filename=image_name,
                                            content_type="image/jpeg")
                        self.data.add_field(name="width",
                                            value="960")
                        self.data.add_field(name="height",
                                            value="640")
                        self.data.add_field(name="cm",
                                            value="100672")
                        self.data.add_field(name="id",
                                            value="WU_FILE_0")
                        self.data.add_field(name="name",
                                            value=image_name)
                        self.data.add_field(name="type",
                                            value="image/jpeg")
                        self.data.add_field(name="size",
                                            value=str(os.path.getsize(answer_image_path)))
                        gmt_format = '%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)'
                        self.data.add_field(name="lastModifiedDate",
                                            value=time.strftime(gmt_format, time.localtime(
                                                int(os.path.getmtime(answer_image_path))
                                            )))
                    else:
                        self.can_request = False
        except Exception as e:
            self.task.exception(str(e))
            self.can_request = False

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errorNo"] == "0":
            url = parse.unquote(text_json["url"])
            for answer_idx, answer in enumerate(self.config.answer):
                if answer == self.invoke_config.tag:
                    self.config.answer[answer_idx] = _IMAGE_PATTERN.format(url, thirteen_digits_time())
                    return True
            return False
        return False
