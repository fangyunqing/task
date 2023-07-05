# @Time    : 2023/07/03 14:04
# @Author  : fyq
# @File    : bai_jia_hao.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import random
from dataclasses import dataclass
from typing import Union, List, Optional

from aiohttp import ClientResponse
from munch import Munch

from core import constant
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.chatgpt import invoke_3d5_turbo
from core.util.guid import guid32
import pyparsing as pp


@dataclass
class ArticleImage:
    data: dict = None

    html_format = ('<p style="text-align: center" '
                   'data-bjh-caption-id="cap-{}" '
                   'class="bjh-image-container cant-justify" '
                   'data-bjh-helper-id="{}" '
                   'data-bjh-caption-text="" '
                   'data-bjh-caption-length="16"> '
                   '<img src="{}" '
                   'data-bjh-origin-src="{}" '
                   'data-bjh-type="IMG" '
                   'data-bjh-params="{"is_legal":1,"index":1,"credit_line":"{}","res_id":"{}","asset_family":"{}"}" '
                   'data-diagnose-id="{}" '
                   'data-bjh-text-align="center" '
                   'data-w="{}" '
                   'data-h="{}">'
                   '</p>'
                   )

    @property
    def html(self):
        params = [
            random.randint(60000000, 99999999),
            guid32(),
            self.data.get("detail_url"),
            self.data.get("credit_line"),
            self.data.get("res_id"),
            self.data.get("asset_family"),
            guid32(),
            self.data.get("w"),
            self.data.get("h")
        ]

        return self.html_format.format(params)


class PictureSearchApi(AbstractApi):
    url = "https://baijiahao.baidu.com/aigc/bjh/pc/v1/picSearch"
    method = constant.hm.post_data
    api_types = ['bai_jia_hao_baidu']
    task_types = [constant.kw.schedule]

    async def _before(self):
        self.data = {
            "keyword": self.invoke_config.keyword,
            "page_no": 0,
            "page_size": 3,
            "label": "superior"
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        text_json = json.loads(text)
        if text_json["errno"] == 0:
            image_list = text_json["data"]["imglist"]
            if len(image_list) > 0:
                self.config.article["image"][self.invoke_config.keyword] = random.choice(image_list)
                return True
            else:
                return False
        else:
            return False


class SaveApi(AbstractApi):
    url = "https://baijiahao.baidu.com/aigc/bjh/pc/v1/picSearch?callback=bjhpreview"
    method = constant.hm.post_data
    api_types = ['bai_jia_hao_baidu']
    task_types = [constant.kw.schedule]

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        self.config.article = Munch({
            "images": {}
        })
        data = await invoke_3d5_turbo("我希望你充当医美专家，"
                                      "能够普及关于医美任何方面的知识。"
                                      "首先创作一篇关于医美知识的文章。"
                                      "文章包含标题、小标题、图片,用<标题/小标题/图片:关键词>格式标出")
        title_tag = pp.Suppress("<标题:") + pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums) + pp.Suppress(">")
        little_title_tag = pp.Suppress("<小标题:") + pp.Word(pp.pyparsing_unicode.alphanums) + pp.Suppress(">")
        image_tag = pp.Suppress("<图片:") + pp.Word(pp.pyparsing_unicode.alphanums) + pp.Suppress(">")
        data_lines = data.a.split()
        for line_idx, data_line in enumerate(data_lines.copy()):
            for ps, s, e in title_tag.scan_string(data_line):
                data_lines[line_idx] = "".join(ps)
            for ps, s, e in little_title_tag.scan_string(data_line):
                data_lines[line_idx] = '<h3 data-diagnose-id="{}">{}</h3>'.format(guid32(), "".join(ps))
            for ps, s, e in image_tag.scan_string(data_line):
                data_lines[line_idx] = ArticleImage()
                self.config.article.images["".join(ps)] = data_lines[line_idx]
        return [InvokeInfo("PictureSearch", Munch({"keyword": key}))
                for key in self.config.article.images.keys()]

    async def _before(self):
        self.data = {
            "type": "news",
            "title": "",
            "content": "",
            "abstract": "",
            "cate_user_cms[0]": "医美",

        }

    async def _after(self, response: ClientResponse) -> bool:
        pass
