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

from core import constant, chatgpt, record
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi, AbstractNodeApi
from core.api.baidu.util import utdata
from core.util.time import thirteen_digits_time, get_date

_IMAGE_SOURCE = "https://source.unsplash.com/960x640/?"

_QUESTION_IMAGE_PATTERN = ("你是一个资深的答主，"
                           "帮我回答关于「{}」的问题，要求答案包含相关图片，字数在200到300之间，"
                           "显示图片请用markdown语法 (" + _IMAGE_SOURCE + "<英文关键词>)。")
_QUESTION_PATTERN = ("你是一个资深的答主，"
                     "帮我回答关于「{}」的问题，字数在200到300之间。")
_IMAGE_PATTERN = '<p><img src="{}" data_time="{}"/></p>'


def _q_format(q):
    if 0 <= random.randint(0, 2) <= 2:
        return _QUESTION_IMAGE_PATTERN.format(q)
    else:
        return _QUESTION_PATTERN.format(q)


class ChoiceApi(AbstractNodeApi):
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    api_names = [
        "homepage",
    ]
    active_api = None

    async def _ready_data(self):
        self.config.record = record.get_record(Munch({"kind": "baidu", "name": "question", "date": get_date()}))
        self.active_api = random.choice(self.api_names)
        for file in glob.glob(f"{self.task.opt.image_path}{os.sep}answer{os.sep}*"):
            os.remove(file)

    def _next(self):
        if self.config.record.num < 300:
            return InvokeInfo(self.active_api)


class GetQList319Api(AbstractApi):
    url = "https://zhidao.baidu.com/activity/ajax/getqlist"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    ASK_PATTERN = "[{}]问题是否询问习俗还是节日?节日回复1,风俗回复2,都是不是回复3"
    HOLIDAY_PATTERN = "{},节日由来,相关典故,寓意,庆祝方式,相关扩展"
    CUSTOM_PATTERN = "{},习俗的详细介绍/来源解释,列举相关习俗案例,相关扩展"

    async def _before(self, session):
        self.data = {
            "packageId": 319
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            question_list = text_json["data"]["list"]
            q_len = len(question_list)
            if q_len > 0:
                question = question_list[random.randint(0, q_len - 1)]

                ask_answer = await chatgpt.invoke_3d5_turbo(self.ASK_PATTERN.format(question['qTitle']))
                if ask_answer is None or ask_answer.a == "3":
                    self.config.question = _q_format(f"{question['qTitle']}")
                elif ask_answer.a == "2":
                    self.config.question = _q_format(self.CUSTOM_PATTERN.format(f"{question['qTitle']}"))
                else:
                    self.config.question = _q_format(
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
    tags = ["动漫",
            "节日",
            "习俗",
            "生活常识",
            "人际交往",
            "法律",
            "文学",
            "历史",
            "哲学",
            "健身",
            "养生保健",
            "婚姻继承"]

    async def _before(self, session):
        self.data = {
            "pn": 20 * random.randint(0, 5),
            "rn": 20,
            "ie": "utf8",
            "type": "highScore",
            "tag": random.choice(self.tags),
            "cid": "",
            "keyWord": "",
            "category": "",
            "t": thirteen_digits_time()
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            question_list = [q for q in text_json["data"]["list"] if q["picFlag"] == 0]
            q_len = len(question_list)
            if q_len > 0:
                score_question = [q for q in question_list if q["score"] > 0]
                if len(score_question) > 0:
                    question = score_question[random.randint(0, len(score_question) - 1)]
                else:
                    question = question_list[random.randint(0, q_len - 1)]
                # 不回答图片的问题
                if question.setdefault("contentRich", None):
                    return False
                content: str = question['content'].strip()
                title: str = question['title'].strip()
                if content or title:
                    self.config.question = _q_format(f"{title}.{content}")
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
            answer = await chatgpt.invoke_3d5_turbo(question=self.config.question, log=self.task.info)
            if answer is None or len(answer.a) < 10:
                self.can_request = False
                return
            tag = pp.OneOrMore(pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + "'.,+-*!#$%&"))
            pp_url = pp.Literal("(") + pp.Literal(_IMAGE_SOURCE) + tag + pp.Literal(")")
            answers = []
            urls = []
            idx = 0
            for ps_idx, (u, s, e) in enumerate(pp_url.scan_string(answer.a)):
                urls.append("".join(u)[1:-1])
                sub: str = answer.a[idx:s]
                sub_idx = sub.find("![")
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

    async def _before(self, session):
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
                if not self.config.task_sign:
                    self.data["taskfr"] = "taskSign"
            except Exception as e:
                self.task.exception(str(e))

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errorNo"] == "0":
            self.config.record.num += 1
            record.update_record(self.config.record)
        return True

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("myanswer")


class MyAnswerApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/myanswer"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    appeal = None

    async def _before(self, session):
        self.data = {
            "pn": 0,
            "rn": 20,
            "t": thirteen_digits_time(),
            "type": "default"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        self.appeal = None
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
                    self.appeal = Munch({
                        "qid": question["qid"],
                        "aid": question["replyId"]
                    })
                    return True
            return False
        else:
            return False

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if self.appeal:
            return InvokeInfo("appeal", self.appeal)

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("mytask")

    def fail(self) -> Optional[InvokeInfo]:
        return InvokeInfo("mytask")


class AppealApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self, session):
        self.data = {
            "cm": 100043,
            "qid": self.invoke_config.qid,
            "type": 100009,
            "aid": self.invoke_config.aid,
            "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
            "stoken": self.config.login["stoken"]
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        pass


class UploadImageApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self, session):
        try:
            async with aiohttp.ClientSession() as session:
                image_url = self.invoke_config.url
                while True:
                    async with session.get(url=image_url, allow_redirects=False) as response:
                        if response.status == 302:
                            redirect_url = response.headers["Location"]
                            if "source-404" in redirect_url:
                                self.can_request = False
                                break
                            image_url = redirect_url
                        elif response.status == 200:
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
                            break
                        else:
                            self.can_request = False
                            break
        except Exception as e:
            self.task.exception(str(e))
            self.can_request = False

    async def _after(self, response: ClientResponse, session) -> bool:
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


class MyTaskApi(AbstractApi):
    url = "https://zhidao.baidu.com/task/api/mytask"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    task_id_list = []
    task_name_list = ["conDailyTask", "dailyTask", "growupTask"]
    task_sign = "taskSignInfo"

    async def _before(self, session):
        self.data = {
            "fr": "pc",
            "_": thirteen_digits_time()
        }

    def handle_task(self, task):
        if isinstance(task, list):
            for sub_task in task:
                if "target" in sub_task and "taskProgress" in sub_task and "taskStatus" in sub_task:
                    task_status = sub_task["taskStatus"]
                    # 2代表问题已经回答完毕 可以领取
                    if task_status == 2 and "taskId" in sub_task:
                        self.task_id_list.append(sub_task["taskId"])
                    if sub_task["name"]:
                        task_name = sub_task["name"]
                        if task_name == "点赞":
                            if task_status == 1:
                                self.config.like = False
                            else:
                                self.config.like = True
                        elif task_name == "评论":
                            if task_status == 1:
                                self.config.comment = False
                            else:
                                self.config.comment = True
        elif isinstance(task, dict):
            for _, sub_task in task.items():
                self.handle_task(sub_task)

    async def _after(self, response: ClientResponse, session) -> bool:
        self.task_id_list = []
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            for task_name, task in text_json["data"].items():
                if task_name in self.task_name_list:
                    self.handle_task(task)
                if task_name == self.task_sign:
                    if isinstance(task, list) and len(task) > 0:
                        sub_task = task[0]
                        if sub_task["status"] == 1:
                            self.config.task_sign = False
                        else:
                            self.config.task_sign = True
                    else:
                        self.config.task_sign = True
            return True
        else:
            return False

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        return [InvokeInfo("tasksubmit", Munch({"task_id": task_id})) for task_id in self.task_id_list]

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("question")

    def fail(self) -> Optional[InvokeInfo]:
        return InvokeInfo("question")


class TaskSubmit(AbstractApi):
    url = "https://zhidao.baidu.com/task/submit/getreward"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self, session):
        self.data = {
            "stoken": self.config.login["stoken"],
            "taskId": self.invoke_config.task_id
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        pass


class QuestionApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/push"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    q = None

    async def _before(self, session):
        self.data = {
            "pn": 0,
            "rn": 20,
            "type": "newRecommend",
            "keyInTag": "1",
            "filter": "",
            "t": thirteen_digits_time(),
            "tag": "",
            "isMavin": "",
            "vcode_str": "",
            "vcode": "",
            "isAll": "",
            "isExpGroup": ""
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            q_list = text_json["data"]["detail"]
            q_list = [q for q in q_list
                      if q["replyNum"] > 0]
            if len(q_list) > 0:
                self.q = random.choice(q_list)
                return True
            else:
                return False
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("viewquestion", Munch(self.q))


class ViewQuestionApi(AbstractApi):
    url = "https://zhidao.baidu.com/question/{}.html?entry=qb_uhome_tag"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    aid_list = []

    async def _before(self, session):
        self.url = self.url.format(self.invoke_config.qid)

    async def _after(self, response: ClientResponse, session) -> bool:
        self.aid_list = []
        try:
            text = await response.text(encoding="utf-8")
        except UnicodeDecodeError:
            return False
        u = (
                pp.Literal("answer-content-") + pp.Word(pp.nums, exact=10)
        )
        for ps, _, _ in u.scan_string(text):
            self.aid_list.append("".join(ps).replace("answer-content-", ""))
        return True

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        invoke_list = []
        if self.aid_list:
            if not self.config.like:
                invoke_list.append(InvokeInfo("like", Munch({"qid": self.invoke_config.qid,
                                                             "aid": random.choice(self.aid_list)})))
            if not self.config.comment:
                invoke_list.append(InvokeInfo("comment", Munch({"qid": self.invoke_config.qid,
                                                                "aid": random.choice(self.aid_list)})))
        return invoke_list

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("showlottery")


class LikeApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.post_data
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self, session):
        self.data = {
            "cm": "100669",
            "qid": self.invoke_config.qid,
            "aid": self.invoke_config.aid,
            "type": 1,
            "utdata": utdata.utdata(thirteen_digits_time(), thirteen_digits_time()),
            "stoken": self.config.login["stoken"]
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        return True


class CommentApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/comment/comment"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    comment_list = ["不错", "很好,是我需要的", "厉害啊我的哥"]

    async def _before(self, session):
        self.data = {
            "qid": self.invoke_config.qid,
            "rid": self.invoke_config.aid,
            "content": random.choice(self.comment_list),
            "stoken": self.config.login["stoken"],
            "from": "pc",
            "_": thirteen_digits_time()
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        return True


class ShowLotteryApi(AbstractApi):
    url = "https://zhidao.baidu.com/shop/lottery"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]
    lucky_token = None
    free_chance = None

    async def _before(self, session):
        pass

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        lucky_token_word = (pp.Suppress("F.context('luckyToken', '") +
                            pp.Word(pp.alphanums + "._-*=") +
                            pp.Suppress("');"))
        lucky_token_list = list(lucky_token_word.scan_string(text))
        assert len(lucky_token_list) == 1
        token, s, e = lucky_token_list[0]
        self.lucky_token = token[0]

        free_chance_word = (pp.Suppress("F.context('freeChance', '") +
                            pp.Word(pp.nums + "-") +
                            pp.Suppress("');"))
        free_chance_list = list(free_chance_word.scan_string(text))
        assert len(free_chance_list) == 1
        free_chance, s, e = free_chance_list[0]
        self.free_chance = int(free_chance[0])
        return True

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if self.lucky_token and self.free_chance > 0:
            return InvokeInfo("submitlottery", Munch({"lucky_token": self.lucky_token}))


class SubmitLotteryApi(AbstractApi):
    url = "https://zhidao.baidu.com/shop/submit/lottery"
    method = constant.hm.get
    api_types = ['question_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self, session):
        self.data = {
            "type": 0,
            "token": self.invoke_config.lucky_token,
            "_": thirteen_digits_time()
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] != 0:
            self.task.error(text_json["errmsg"])
            return False
        else:
            return True
