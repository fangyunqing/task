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
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, List, Union
from urllib import parse

import aiohttp
import pyparsing as pp
from PIL import ImageGrab
from aiohttp import ClientResponse
from munch import Munch

from core import constant, chatgpt, record
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi, AbstractNodeApi
from core.api.baidu.util import utdata
from core.util.time import thirteen_digits_time, get_date
import xlwings as xl

_IMAGE_SOURCE = "https://source.unsplash.com/960x640/?"

_QUESTION_IMAGE_PATTERN = ("你是一个资深的答主，"
                           "帮我回答关于「{}」的问题，要求答案包含相关图片，答案能够通过AI内容检测工具检测，"
                           "显示图片请用markdown语法 (" + _IMAGE_SOURCE + "<英文关键词>)。")
_QUESTION_PATTERN = ("你是一个资深的答主，"
                     "帮我回答关于「{}」的问题，字数在200到300之间。")

_NEW_IMAGE_PATTERN = ("你是一个资深的答主，"
                      "帮我回答关于[{}]的问题，至少100字，答案不包含任何网址，不要瞎编；"
                      "答案至少包含一个图片标签，显示图片标签用格式<图片：中文关键字>，图片无序。")


@dataclass
class QuestionImage:
    keyword: str

    data: Munch = field(default_factory=lambda: Munch())

    pattern = ('<p iknow-image-from-bjh="1">'
               '<img src="{}" data_time="{}" data_resid="{}" data_pwtype="{}" data_picurl="{}"/>'
               '</p>')

    @cached_property
    def html(self):
        h = self.pattern.format(
            self.data.setdefault("url", constant.kw.MISSING),
            thirteen_digits_time(),
            self.data.setdefault("res_id", ""),
            self.data.setdefault("pwType", ""),
            self.data.setdefault("detail_url", constant.kw.MISSING)
        )
        if constant.kw.MISSING not in h:
            return h


def _q_format(q):
    if 0 <= random.randint(0, 2) <= 2:
        return _NEW_IMAGE_PATTERN.format(q)
    else:
        return _QUESTION_PATTERN.format(q)


class ChoiceApi(AbstractNodeApi):
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    api_names = [
        ("homepage", range(0, 5)),
        ("push", range(5, 25)),
        ("package322", range(25, 40))
    ]
    active_api = None

    async def _ready_data(self):
        self.config.record = record.get_record(Munch({"kind": "baidu", "name": "question", "date": get_date()}))
        weight = random.randint(0, 40)
        for api_name, weight_list in self.api_names:
            if weight in weight_list:
                self.active_api = api_name
                break
        for file in glob.glob(f"{self.task.opt.image_path}{os.sep}answer{os.sep}*"):
            os.remove(file)

    def _next(self):
        if self.config.record.num < 300:
            return InvokeInfo(self.active_api)


class HomePageApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/homepage"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
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

                self.config.question = _q_format(f"{question['title'].strip()}.{question['content'].strip()}")
                self.config.entry = "list_highScore_all"
                self.config.qid = question["qid"]
                return True
            else:
                return False
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("submitajax2")


class PushApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/push"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    tags = [
        "两性健康",
        "习俗",
        "节日",
        "医学常识",
        "金融常识",
        "经济学常识",
        "健康常识",
        "生活常识",
        "人际交往",
        "亲情",
        "爱情",
        "成语",
        "儿童文学",
        "四大名著",
    ]

    async def _before(self, session):
        self.data = {
            "pn": 20 * random.randint(0, 5),
            "rn": 20,
            "type": "newRecommend",
            "keyInTag": "1",
            "filter": "",
            "t": thirteen_digits_time(),
            "tags": random.choice(self.tags),
            "isMavin": "0",
            "vcode_str": "",
            "vcode": "",
            "isAll": "0",
            "isExpGroup": "0"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERRNO] == 0:
            question_list = text_json["data"]["detail"]
            question_list = [q
                             for q in question_list
                             if q["hasPic"] == 0 and q["isVideo"] == 0]
            q_len = len(question_list)
            if q_len > 0:
                score_question = [q for q in question_list if q["score"] > 0]
                if len(score_question) > 0:
                    question = score_question[random.randint(0, len(score_question) - 1)]
                else:
                    question = question_list[random.randint(0, q_len - 1)]

                self.config.question = _q_format(f"{question['title'].strip()}.{question['content'].strip()}")
                self.config.entry = "uhome_homecenter_myTag"
                self.config.qid = question["qid"]
                return True
            else:
                self.task.warning(f"{self.data['tags']}是返回空列表")
                return False
        else:
            self.task.error(text_json[constant.error.ERRMSG])
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("submitajax2")


class SubmitAjax2Api(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if len(self.config.question) <= 5:
            self.can_request = False
            return

        answer = await chatgpt.invoke_3d5_turbo(question=self.config.question, log=self.task.info)
        if answer is None or len(answer.a) < 10:
            self.can_request = False
            return

        image_tag = (
                pp.Suppress("<图片：") +
                pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + '''、：:，,!！.。;；：:'‘“"?？《》''') +
                pp.Suppress(">")
        )

        self.config.answer = []
        self.config.images = []
        for line_idx, data_line in enumerate(answer.a.split('\n')):
            parse_result_list = list(image_tag.scan_string(data_line))
            if len(parse_result_list) == 0:
                self.config.answer.append(data_line)
            else:
                idx = 0
                for ps, s, e in parse_result_list:
                    sub_data = data_line[idx:s]
                    idx = e
                    if sub_data:
                        self.config.answer.append(sub_data)
                    self.config.answer.append(QuestionImage(keyword="".join(ps)))
                    self.config.images.append(self.config.answer[-1])
                sub_data = data_line[idx:]
                if sub_data:
                    self.config.answer.append(sub_data)

        invokes = []
        for image in self.config.images:
            invokes.append(InvokeInfo("picturequery", Munch({"question_image": image})))
            invokes.append(InvokeInfo("pictureurlcommit", Munch({"question_image": image})))
            invokes.append(InvokeInfo("submitimage", Munch({"question_image": image})))
        return invokes

    async def _before(self, session):
        if self.can_request:
            try:
                content_lines = []
                for a in self.config.answer:
                    if isinstance(a, str):
                        if len(a) > 0:
                            content_lines.append("<p>{}</p>".format(a))
                        else:
                            content_lines.append("<p><br></p>")
                    elif isinstance(a, QuestionImage):
                        if a.html:
                            content_lines.append(a.html)

                if len(content_lines) == 0:
                    self.can_request = False
                    return

                self.data = {
                    "cm": 100009,
                    "qid": self.config.qid,
                    "title": "",
                    "answerfr": "",
                    "feedback": 0,
                    "entry": self.config.entry,
                    "co": f"<p>{''.join(content_lines)}<p>",
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
        if text_json[constant.error.ERROR_NO] == "0":
            self.config.record.num += 1
            record.update_record(self.config.record)
        else:
            if constant.error.ERROR_MSG in text_json:
                self.task.error(text_json[constant.error.ERROR_MSG])
        return True

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("myanswer")


class SubmitAjaxApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax/"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if len(self.config.question) < 5:
            self.can_request = False
            return

        answer = await chatgpt.invoke_3d5_turbo(question=self.config.question, log=self.task.info)
        if answer is None or len(answer.a) < 10:
            self.can_request = False
            return

        answer_a = json.loads(answer.a)
        assert "answer" in answer_a
        trans = answer_a["answer"]
        assert isinstance(trans, list) and 2 <= len(trans) <= 3

        m_list = []
        for v1 in trans:
            m = Munch()
            m_list.append(m)
            assert "词汇" in v1
            assert isinstance(v1["词汇"], str)
            m.word = v1["词汇"]

            assert "词性" in v1
            assert isinstance(v1["词性"], str)
            m.pos = v1["词性"]

            assert "含义" in v1
            assert isinstance(v1["含义"], str)
            m.meaning = v1["含义"]

            assert "发音" in v1
            assert isinstance(v1["发音"], dict)
            m.pronunciation = Munch()
            assert "英式发音" in v1["发音"]
            assert "美式发音" in v1["发音"]
            for k2, v2 in v1["发音"].items():
                if k2 == "英式发音":
                    m.pronunciation.uk = v2
                elif k2 == "美式发音":
                    m.pronunciation.us = v2

            assert "语句详解" in v1
            assert isinstance(v1["语句详解"], str)
            m.sentence = v1["语句详解"]

            assert "用法简介" in v1
            assert isinstance(v1["用法简介"], str)
            m.lit = v1["用法简介"]

            assert "用法" in v1
            assert isinstance(v1["用法"], list)
            m.usage = []
            u_set = set()
            for uu in v1["用法"]:
                assert isinstance(uu, dict)
                assert "英文" in uu
                assert "中文" in uu
                assert "用法详解" in uu
                mm = Munch()
                mm.zh = uu["中文"]
                mm.en = uu["英文"]
                mm.use = uu["用法详解"]
                u_set.add(mm.use)
                assert "用法示例" not in mm.use
                m.usage.append(mm)
            assert len(u_set) == len(m.usage)
        assert 2 <= len(m_list) <= 3

        app = xl.App(visible=False, add_book=False)
        try:
            wb = app.books.open(f"{self.task.opt.template_path}{os.sep}translate.xlsx")
            try:
                sheet = wb.sheets[0]
                b = 65
                for m_idx, m in enumerate(m_list):
                    b += 1
                    s_b = chr(b)
                    sheet.range(f"{s_b}1").value = m.word
                    sheet.range(f"{s_b}2").value = m.meaning
                    sheet.range(f"{s_b}3").value = "\n".join([f"{k}：【{v}】" for k, v in m.pronunciation.items()])
                    sheet.range(f"{s_b}4").value = m.lit

                    for rng in [f"{s_b}1", f"{s_b}2", f"{s_b}3", f"{s_b}4"]:
                        r = sheet.range(rng)
                        r.column_width = 25
                        r.wrap_text = 24
                        r.rows.autofit()
                        if r.row_height < 24:
                            r.row_height = 24

                rng = sheet.range(f"A1:{chr(b)}4")
                rng.api.CopyPicture()
                time.sleep(2)
                sheet.api.Paste()
                image_path = f"{self.task.opt.image_path}{os.sep}answer{os.sep}{uuid.uuid1()}.png"
                pic = sheet.pictures[0]
                pic.api.Copy()
                time.sleep(2)
                img = ImageGrab.grabclipboard()
                w = img.width
                h = img.height
                img.save(image_path)
                pic.delete()
            finally:
                wb.close()
        finally:
            app.quit()

        self.config.answer = m_list
        self.config.images = [Munch({"image_path": image_path, "type": "png", "w": w, "h": h})]
        return [InvokeInfo("uploadimage", image) for image in self.config.images]

    async def _before(self, session):
        if self.can_request:
            try:
                word_list = [m.word for m in self.config.answer]
                if len(word_list) > 2:
                    all_word = f"{'、'.join(word_list[0:-1])}和{word_list[-1]}"
                else:
                    all_word = '和'.join(word_list)
                content_list = [f"<p><strong>首先我们来看下{all_word}的大致意思：</strong></p>"]
                for m in self.config.answer:
                    content_list.append(f"<p><strong>{m.word}：词性为{m.pos}，{m.sentence}</strong></p>")
                content_list.append(f"<p>通过下面的表格我们了解下{all_word}的含义、发音和用法</p>")
                content_list.append(self.config.images[0].format)
                content_list.append("<hr/>")
                content_list.append(f"<p><strong>接下来让我们看下{all_word}的用法区别：</strong></p>")

                for m in self.config.answer:
                    content_list.append("<br/>")
                    content_list.append(f"<p>🚀🚀🚀 <strong>{m.word}</strong> 🚀🚀🚀</p>")
                    content_list.append("<hr/>")
                    for u in m.usage:
                        content_list.append(f"<p><strong>用法详解：{u.use}</strong></p>")
                        content_list.append(f"<p><strong>例子：</strong></p>")
                        content_list.append(f"<p>- <strong>{u.en}</strong></p>")
                        content_list.append(f"<p>({u.zh})</p>")

                self.data = {
                    "cm": 100009,
                    "qid": self.config.qid,
                    "title": "",
                    "answerfr": "",
                    "feedback": 0,
                    "entry": self.config.entry,
                    "co": "".join(content_list),
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
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
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
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

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
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    _IMAGE_PATTERN = '<p><img src="{}" data_time="{}"/></p>'

    async def _before(self, session):
        image_name = os.path.basename(os.path.normpath(self.invoke_config.image_path))
        self.data: aiohttp.FormData = aiohttp.FormData()
        self.data.add_field(name="image",
                            value=open(self.invoke_config.image_path, "rb"),
                            filename=image_name,
                            content_type=f"image/{self.invoke_config.type}")
        self.data.add_field(name="width",
                            value=str(self.invoke_config.w))
        self.data.add_field(name="height",
                            value=str(self.invoke_config.h))
        self.data.add_field(name="cm",
                            value="100672")
        self.data.add_field(name="id",
                            value="WU_FILE_0")
        self.data.add_field(name="name",
                            value=image_name)
        self.data.add_field(name="type",
                            value=f"image/{self.invoke_config.type}")
        self.data.add_field(name="size",
                            value=str(os.path.getsize(self.invoke_config.image_path)))
        gmt_format = '%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)'
        self.data.add_field(name="lastModifiedDate",
                            value=time.strftime(gmt_format,
                                                time.localtime(
                                                    int(os.path.getmtime(self.invoke_config.image_path))
                                                )
                                                )
                            )

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errorNo"] == "0":
            url = parse.unquote(text_json["url"])
            self.invoke_config.format = self._IMAGE_PATTERN.format(url, thirteen_digits_time())
            self.invoke_config.url = url
        else:
            return False


class MyTaskApi(AbstractApi):
    url = "https://zhidao.baidu.com/task/api/mytask"
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    task_id_list = []
    task_name_list = ["conDailyTask", "dailyTask", "growupTask", "activityTask"]
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
                        elif task_name == "点赞宝藏回答":
                            if task_status == 1:
                                self.config.approval_treasure = False
                            else:
                                self.config.approval_treasure = True

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
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "stoken": self.config.login["stoken"],
            "taskId": self.invoke_config.task_id
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        pass


class QuestionApi(AbstractApi):
    url = "https://zhidao.baidu.com/ihome/api/push"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    q = None

    async def _before(self, session):
        self.data = {
            "pn": 0,
            "rn": 20,
            "type": "newRecommend",
            "keyInTag": "1",
            "filter": "",
            "t": thirteen_digits_time(),
            "tags": "",
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
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
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
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

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
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
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
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
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
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

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


class PictureQueryApi(AbstractApi):
    url = "https://baijiahao.baidu.com/aigc/bjh/pc/v1/picSearch"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "page_no": 0,
            "page_size": 20,
            "keyword": self.invoke_config.question_image.keyword
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERRNO] == 0:
            image_list = text_json["data"]["imglist"]
            if len(image_list) > 0:
                self.invoke_config.question_image.data.update(random.choice(image_list))
                self.invoke_config.question_image.data.pwType = "sjzg"
                return True
            else:
                return False
        else:
            self.task.error(text_json[constant.error.ERRMSG])
            return False


class PictureUrlCommitApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/picture/picurlcommit"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "picUrl": self.invoke_config.question_image.data.detail_url,
            "pwType": self.invoke_config.question_image.data.pwType
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERRNO] == 0:
            self.invoke_config.question_image.data.update(text_json["data"])
            return True
        else:
            self.task.error(text_json[constant.error.ERRMSG])
            return False


class SubmitImageApi(AbstractApi):
    url = "https://zhidao.baidu.com/submit/ajax"
    method = constant.hm.POST_DATA
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "cm": 100682,
            "picUrl": self.invoke_config.question_image.data.url
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERROR_NO] == "0":
            self.invoke_config.question_image.data.url = text_json["url"]
            return True
        else:
            self.task.error(text_json[constant.error.ERROR_MSG])
            return False


class Package322(AbstractApi):
    url = "https://zhidao.baidu.com/activity/ajax/getqlist"
    method = constant.hm.GET
    api_types = ['question_baidu']
    task_types = [constant.kw.SCHEDULE]
    format = ('你是一名资深的答主，'
              '帮我回答问题【question】,'
              '答案包含词汇、词性、含义、发音、语句详解、用法简介、用法。'
              '其中用法至少包含3个用法示例，每个用法包含用法详解、中文、英文；'
              '其中发音包含英式发音和美式发音。'
              '注意答案格式为JSON，这个是规则，请必须遵守，'
              '格式像这样的 {"answer": [{'
              '"词汇": ?, '
              '"词性": ?, '
              '"含义": ?, '
              '"发音": {"英式发音": ?, "美式发音": ?}, '
              '"用法简介":?, '
              '"语句详解": ?, '
              '"用法": [{"用法详解": ?,"中文": ?,"英文": ?}]'
              '}...]'
              '}')

    async def _before(self, session):
        self.data = {
            "packageId": 322
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json[constant.error.ERRNO] == 0:
            q_list = text_json["data"]["list"]
            if len(q_list) > 0:
                q = random.choice(q_list)
                self.config.question = self.format.replace('question', q["qTitle"])
                self.config.entry = "iknowduck_93"
                self.config.qid = q["encodeQid"]
                return True
            else:
                return False

        else:
            self.task.error(text_json[constant.error.ERRMSG])
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("submitajax")
