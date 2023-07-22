# @Time    : 2023/07/03 14:04
# @Author  : fyq
# @File    : article.py
# @Software: PyCharm

__author__ = 'fyq'

import asyncio
import json
import os
import random
import uuid
from dataclasses import dataclass
from typing import Union, List, Optional, Any
from urllib.parse import quote

import aiohttp
from aiohttp import ClientResponse
from munch import Munch
from sortedcontainers import SortedKeyList

from core import constant, record
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi, AbstractNodeApi
from core.chatgpt import invoke_3d5_turbo
from core.util.guid import guid32
import pyparsing as pp
from PIL import Image

from core.util.time import get_date, thirteen_digits_time


@dataclass
class ArticleImage:
    data: dict = None

    valid = True

    html_format = ('<p style="text-align: center" '
                   'data-bjh-caption-id="cap-{}" '
                   'class="bjh-image-container cant-justify" '
                   'data-bjh-helper-id="{}" '
                   'data-bjh-caption-text="" '
                   'data-bjh-caption-length="16"> '
                   '<img src="{}" '
                   'data-bjh-origin-src="{}" '
                   'data-bjh-type="IMG" '
                   'data-bjh-params="{}" '
                   'data-diagnose-id="{}" '
                   'data-bjh-text-align="center" '
                   'data-w="{}" '
                   'data-h="{}">'
                   '</p>'
                   )

    @property
    def html(self):
        bjh_params = {
            "is_legal": 1,
            "index": 1,
            "credit_line": self.data.get("credit_line"),
            "res_id": self.data.get("res_id"),
            "asset_family": self.data.get("asset_family")
        }

        params = (
            random.randint(10000000, 99999999),
            thirteen_digits_time(),
            self.data.get("detail_url"),
            self.data.get("detail_url"),
            quote(json.dumps(bjh_params)),
            guid32(),
            self.data.get("w"),
            self.data.get("h")
        )

        return self.html_format.format(*params)


@dataclass
class ArticleLittleTitle:
    title: str

    html_format = '<h3 data-diagnose-id="{}">{}</h3>'

    @property
    def html(self):
        params = (
            guid32(),
            self.title
        )

        return self.html_format.format(*params)


@dataclass
class ImageCut:
    src: str = None

    https_src: str = None

    origin_src: str = None

    crop_data: dict = None

    machine: int = 1

    legal: int = 0


class ArticleApi(AbstractNodeApi):
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]
    kind = [
        ["情感", "心灵鸡汤"],
        ["情感", "人际关系"],
        ["情感", "两性"],
        ["医美", "知识科普"],
        ["医美", "医美综合"],
    ]

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        return InvokeInfo("articleedit")

    async def _ready_data(self):
        self.config.article = Munch()
        if not self.config.can_article:
            return
        self.config.record = record.get_record(Munch({"kind": "baidu", "name": "article", "date": get_date()}))

        self.config.kind = random.choice(self.kind)
        topics = await invoke_3d5_turbo("帮我列举几个关于[{}]的话题，要求每个话题长度大于8。"
                                        "回复只包含[topics]的json格式".format("-".join(self.config.kind)),
                                        log=self.task.info)
        if topics:
            topic_dict = json.loads(topics.a)
            if "topics" in topic_dict:
                topics = [topic
                          for topic in topic_dict["topics"]
                          if len(topic) > 7]
                if len(topics) > 0:
                    await asyncio.sleep(60)
                    title = random.choice(topics)
                    data = await invoke_3d5_turbo('创作一篇主题为[{}]的文章，文章不包含任何网址，能够通过AI内容检测工具检测；'
                                                  '文章包含标题、小标题、图片，使用不同于主题的标题；'
                                                  '显示标题用<标题：中文关键字>；'
                                                  '显示小标题用<小标题：中文关键字>，小标题无序；'
                                                  '显示图片用<图片：中文关键字>，图片无序。'.format(title),
                                                  log=self.task.info)
                    if data and '小标题1' not in data.a and '图片1' not in data.a and data.a.startswith("<标题："):
                        self.config.article.title = title
                        title_tag = (
                                pp.Suppress("<标题：") +
                                pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + '''、：:，,!！.。;；：:'‘“"?？《》''') +
                                pp.Suppress(">")
                                     )
                        little_title_tag = (
                                pp.Suppress("<小标题：") +
                                pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + '''、：:，,!！.。;；：:'‘“"?？《》''') +
                                pp.Suppress(">")
                        )
                        image_tag = (
                                pp.Suppress("<图片：") +
                                pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums + '''、：:，,!！.。;；：:'‘“"?？《》''') +
                                pp.Suppress(">")
                        )
                        data_lines: List[Any] = data.a.split('\n')
                        for line_idx, data_line in enumerate(data_lines.copy()):
                            for ps, s, e in title_tag.scan_string(data_line):
                                data_lines[line_idx] = "".join(ps)
                            for ps, s, e in little_title_tag.scan_string(data_line):
                                data_lines[line_idx] = ArticleLittleTitle(title="".join(ps))
                            for ps, s, e in image_tag.scan_string(data_line):
                                data_lines[line_idx] = ArticleImage()
                                self.config.article.setdefault("images", {})["".join(ps)] = data_lines[line_idx]
                        self.config.article.title = data_lines.pop(0)
                        while len(data_lines) > 0:
                            if data_lines[0] == 0:
                                data_lines.pop(0)
                            else:
                                break
                        self.config.article.content_lines = data_lines

    def _next(self):
        if self.config.article:
            return InvokeInfo("savearticle")

    async def post(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        if self.config.article:
            return [InvokeInfo("picturesearch", Munch({"keyword": key}))
                    for key in self.config.article.images.keys()]


class ArticleEditApi(AbstractApi):
    url = "https://baijiahao.baidu.com/pcui/article/edit"
    method = constant.hm.GET
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "type": "news"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            self.config.can_article = (text_json["data"]["ability"]["publish_num_left"] > 0)
            return True
        else:
            self.task.error(text_json["errmsg"])
            self.config.can_article = False
            return False


class PictureSearchApi(AbstractApi):
    url = "https://baijiahao.baidu.com/aigc/bjh/pc/v1/picSearch"
    method = constant.hm.POST_DATA
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "keyword": self.invoke_config.keyword,
            "page_no": 0,
            "page_size": 20,
            "label": "superior"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            image_list = text_json["data"]["imglist"]
            if len(image_list) > 0:
                self.config.article.images[self.invoke_config.keyword].data = random.choice(image_list)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            url=self.config.article.images[self.invoke_config.keyword].data["detail_url"]) as response:
                        image_path = f"{self.task.opt.image_path}{os.sep}article"
                        if not os.path.exists(image_path):
                            os.makedirs(image_path)
                        image_name = f"{uuid.uuid1()}.jpg"
                        answer_image_path = f"{image_path}{os.sep}{image_name}"
                        with open(answer_image_path, 'wb') as fp:
                            fp.write(await response.read())
                        img = Image.open(answer_image_path)
                        self.config.article.images[self.invoke_config.keyword].data["w"] = img.width
                        self.config.article.images[self.invoke_config.keyword].data["h"] = img.height
                return True
            else:
                self.config.article.images[self.invoke_config.keyword].valid = False
                return False
        else:
            return False


class SaveArticleApi(AbstractApi):
    url = "https://baijiahao.baidu.com/pcui/article/save?callback=bjhpreview"
    method = constant.hm.POST_DATA
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        self.config.article.cover = []
        images = [img for img in self.config.article.images.values() if img.valid]
        if len(images) == 0:
            self.can_request = False
        else:
            invokes = [InvokeInfo("cutpicture", Munch(img.data)) for img in images]
            invokes.append(InvokeInfo("tasksystem"))
            return invokes

    async def _before(self, session):
        if len(self.config.article.cover) == 0:
            self.can_request = False
            return

        if 1 <= len(self.config.article.cover) <= 2:
            cover_images = [self.config.article.cover[0]]
            cover = {
                "cover_layout": "one",
            }
        else:
            cover_images = self.config.article.cover[0:3]
            cover = {
                "cover_layout": "three",
            }
        cover["cover_source"] = "upload"
        cover["cover_images"] = json.dumps([{"src": cover_image.src,
                                             "cropData": cover_image.crop_data,
                                             "machine_chooseimg": cover_image.machine,
                                             "isLegal": cover_image.legal
                                             }
                                            for cover_image in cover_images])
        cover["_cover_images_map"] = json.dumps([{"src": cover_image.src,
                                                  "origin_src": cover_image.origin_src}
                                                 for cover_image in cover_images])
        content_lines = []
        for content_line in self.config.article.content_lines:
            if isinstance(content_line, str):
                if len(content_line) > 0:
                    content_lines.append("<p>{}</p>".format(content_line))
                else:
                    content_lines.append("<p><br></p>")
            elif isinstance(content_line, ArticleImage):
                if content_line.valid:
                    content_lines.append(content_line.html)
            elif isinstance(content_line, ArticleLittleTitle):
                content_lines.append(content_line.html)
        content = "".join(content_lines)
        self.data = {
            "type": "news",
            "title": self.config.article.title,
            "content": content,
            "abstract": "",
            "cate_user_cms[0]": self.config.kind[0],
            "cate_user_cms[1]": self.config.kind[1],
            "len": len(content),
            "activity_list[0][id]": "408",
            "activity_list[0][is_checked]": 1,
            "activity_list[1][id]": "ttv",
            "activity_list[1][is_checked]": 1,
            "activity_list[2][id]": "reward",
            "activity_list[2][is_checked]": 1,
            "source_reprinted_allow": 0,
            "isBeautify": "false",
            "usingImgFilter": "false",
            "subtitle": "",
            "bjhtopic_id": "",
            "bjhtopic_info": "",
        }
        if self.config.article.setdefault("task", None):
            self.data["activity_list[3][id]"] = f"task_{self.config.article.task['id']}"
            self.data["activity_list[3][is_checked]"] = 1

        self.data.update(cover)

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            self.config.article.ret = text_json["ret"]
            self.config.record.num += 1
            record.update_record(self.config.record)
            return True
        else:
            return False

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("publisharticle")


class CutPictureApi(AbstractApi):
    url = "https://baijiahao.baidu.com/pcui/Picture/CuttingPic"
    method = constant.hm.POST_DATA
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]
    image_cut = None

    async def _before(self, session):
        self.image_cut = ImageCut()
        self.image_cut.origin_src = self.invoke_config.detail_url
        cut_y = int(self.invoke_config.w * 2 / 3)
        cut_x = int(self.invoke_config.h * 3 / 2)
        if self.invoke_config.h > cut_y:
            self.image_cut.crop_data = {
                "x": 0,
                "y": int((self.invoke_config.h - cut_y) / 2),
                "width": self.invoke_config.w,
                "height": cut_y
            }
        else:
            self.image_cut.crop_data = {
                "x": int((self.invoke_config.w - cut_x) / 2),
                "y": 0,
                "width": cut_x,
                "height": self.invoke_config.h
            }
        self.data = {
            "auto": "false",
            "x": self.image_cut.crop_data["x"],
            "y": self.image_cut.crop_data["y"],
            "w": self.image_cut.crop_data["width"],
            "h": self.image_cut.crop_data["height"],
            "src": self.image_cut.origin_src,
            "type": "news"
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            self.image_cut.https_src = text_json["data"]["https_src"]
            self.image_cut.src = text_json["data"]["src"]
            self.config.article.cover.append(self.image_cut)
            return True
        else:
            return False


class TaskSystemApi(AbstractApi):
    url = "https://baijiahao.baidu.com/author/eco/tasksystem/getSquareMissionList"
    method = constant.hm.GET
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        self.data = {
            "page_no": 1,
            "article_type": 1,
            "page_size": 18,
            "task_attend": 1,
            "task_origin": "market",
            "task_type": ""
        }

    async def _after(self, response: ClientResponse, session) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            task_list = [task for task in text_json["data"]["list"] if task["has_perm"] == 1]
            task_list = SortedKeyList(iterable=task_list, key=lambda task: task["remain_time"])
            if len(task_list) > 0:
                self.config.article.task = task_list[-1]
            return True
        else:
            return False


class PublishArticleApi(AbstractApi):
    url = "https://baijiahao.baidu.com/pcui/article/publish?callback=bjhpublish"
    method = constant.hm.POST_DATA
    api_types = ['article_baidu']
    task_types = [constant.kw.SCHEDULE]

    async def _before(self, session):
        activity_dict = {}
        for activity_idx, activity in enumerate(json.loads(self.config.article.ret["activity_list"])):
            activity_dict[f"activity_list[{activity_idx}][id]"] = activity["id"]
            activity_dict[f"activity_list[{activity_idx}][is_checked]"] = activity["is_checked"]

        self.data = {
            "type": self.config.article.ret["type"],
            "title": self.config.article.ret["title"],
            "content": self.config.article.ret["content"],
            "abstract": self.config.article.ret["abstract"],
            "cate_user_cms[0]": self.config.kind[0],
            "cate_user_cms[1]": self.config.kind[1],
            "len": len(self.config.article.ret["content"]),
            "source_reprinted_allow": 0,
            "isBeautify": "false",
            "usingImgFilter": "false",
            "package_id": "",
            "cover_layout": self.config.article.ret["cover_layout"],
            "cover_images": self.config.article.ret["cover_images"],
            "_cover_images_map": self.config.article.ret["_cover_images_map"],
            "cover_source": self.config.article.ret["cover_source"],
            "subtitle": self.config.article.ret["subtitle"],
            "bjhtopic_id": self.config.article.ret["bjhtopic_id"],
            "bjhtopic_info": self.config.article.ret["bjhtopic_info"],
            "clue": "",
            "bjhmt": "",
            "order_id": "",
            "aigc_rebuild": "",
            "image_edit_point": "",
            "article_id": self.config.article.ret["article_id"]
        }

        self.data.update(activity_dict)

    async def _after(self, response: ClientResponse, session) -> bool:
        pass
