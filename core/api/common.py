# @Time    : 2023/07/25 15:40
# @Author  : fyq
# @File    : common.py
# @Software: PyCharm

__author__ = 'fyq'

import os
import uuid
from abc import ABC

from aiohttp import ClientResponse

from core import constant
from core.api.abstract_api import AbstractApi
from PIL import Image


class AbstractCommonApi(AbstractApi, ABC):
    api_types = [constant.kw.ALL]
    task_types = [constant.kw.ALL]


class CommonImageApi(AbstractCommonApi):
    method = constant.http_method.GET

    async def _before(self, session):
        self.url = self.invoke_config.request_url

    async def _after(self, response: ClientResponse, session) -> bool:
        url_list = os.path.splitext(self.url)
        if len(url_list) > 1:
            image_type: str = url_list[-1][1:]
            image_type = image_type.lower()
            if image_type not in ["png", "jpg", "jpeg"]:
                image_type = "jgp"
        else:
            image_type = "jgp"
        image_path = f"{self.invoke_config.path}{os.sep}{uuid.uuid1()}.{image_type}"
        with open(image_path, "wb") as f:
            f.write(await response.read())
        img = Image.open(image_path)
        self.invoke_config.image_path = image_path
        self.invoke_config.w = img.width
        self.invoke_config.h = img.height
        self.invoke_config.f = img.format

        return True
