# @Time    : 2023/06/02 13:59
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import os
import re
import uuid
from typing import Optional

from urllib import parse

from aiohttp import ClientResponse

from core import constant
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import util1, util6
from core.api.baidu.util.jsonp import jsonp
from core.util import guid, rsa
from core.util.ase import base64_encryption
from core.util.callback import random_callback, jquery_random_call_back
from core.util.format_response import format1
from core.util.time import eleven_digits_time
from settings import IMAGE_PATH


class IndexApi(AbstractApi):
    url = "https://www.baidu.com"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        pass

    async def _after(self, response: ClientResponse) -> bool:
        return True


class GetApiApi(AbstractApi):

    def next(self) -> Optional[str]:
        return "getpublickey"

    def pre(self) -> Optional[str]:
        return "index"

    url = "https://passport.baidu.com/v2/api/?getapi"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        init_data = {
            "apiType": "login",
            "gid": guid.guid(),
            "loginType": "dialogLogin",
            "loginVersion": "v4",
        }
        sign = "getApiInfo"
        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)
        process = {
            "charset": "utf-8",
            "processData": ""
        }

        self.data = jsonp(params=params, process=process)
        self.data[constant.kw.callback] = random_callback()

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.token = m.data.get("token")
        return True


class GetPublicKeyApi(AbstractApi):

    def next(self) -> Optional[str]:
        return "login"

    url = "https://passport.baidu.com/v2/getpublickey"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        init_data = {
            "gid": guid.guid(),
            "loginVersion": "v5",
        }
        sign = "getRsaKey"

        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)

        process = {
            "charset": "utf-8",
            "processData": ""
        }

        self.data = jsonp(params=params, process=process)
        self.data[constant.kw.callback] = random_callback()

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.pubkey = m.get("pubkey", None)
        self.config.key = m.get("key", None)
        return True


class ViewLogApi(AbstractApi):
    url = "https://passport.baidu.com/viewlog"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        if self.config.locus:
            self.data["fk"] = (
                base64_encryption(data=json.dumps(self.config.locus),
                                  key=self.config.store.get("nameL", "") + self.config.store.get("nameR", "")))
        else:
            self.data["fk"] = None
        self.data["ak"] = self.config.store.get("ak", None)
        self.data["as"] = self.config.store.get("nameL", None)
        self.data["tk"] = self.config.store.get("tk", None)
        self.data["scene"] = self.config.store.get("scene", None)
        self.data["cv"] = None
        self.data["_"] = eleven_digits_time()
        self.data[constant.kw.callback] = jquery_random_call_back()

        # clear
        self.config.locus = {}
        self.config.store["ds"] = ""
        self.config.store["tk"] = ""

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.store["ds"] = m.data.get("ds", "")
        self.config.store["as"] = m.data.get("as", "")
        self.config.store["tk"] = m.data.get("tk", "")
        self.config.store["nameL"] = m.data.get("as", "6bffae1c")
        self.config.initTime = self.data["_"]
        return True


class LoginApi(AbstractApi):
    url = "https://passport.baidu.com/v2/api/?login"
    method = constant.hm.post_data
    api_types = ['baidu']
    task_types = [constant.kw.login]
    err_no = None

    def pre(self) -> Optional[str]:
        return "viewlog"

    def _before(self):
        init_data = {
            "codeString": "",
            "detect": "1",
            "gid": guid.guid(),
            "idc": "",
            "isPhone": "",
            "logLoginType": "pc_loginDialog",
            "loginMerge": "true",
            "logintype": "dialogLogin",
            "memberPass": "on",
            "mkey": "",
            "password": rsa.encryption(self.config.pubkey, self.config.account.password),
            "quick_user": "0",
            "safeFlag": "0",
            "splogin": "rate",
            "staticPage": "https://zhidao.baidu.com/static/common/https-html/v3Jump.html",
            "subpro": "",
            "u": "https://zhidao.baidu.com/",
            "userName": self.config.account.username,
            "verifyCode": "",
            "token": self.config.token,
            "rsaKey": self.config.key,
            "crypttype": 12,
            "timeSpan": eleven_digits_time() - self.config.initTime,
            "countrycode": "",
            "FP_UID": "",
            "FP_INFO": "",
            "loginVersion": "v4",
            "supportdv": "1",
            "bdint_sync_cookie": "",
            "ds": self.config.store.get("ds", ""),
            "tk": self.config.store.get("tk", ""),
            "dv": util6.dv_js_input(),
            "fuid": util6.fuid(self.config)

        }
        sign = "login"

        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)
        process = {
            "charset": "utf-8",
            "processData": ""
        }

        self.data = jsonp(params=params, process=process)
        self.data[constant.kw.callback] = "parent." + random_callback()

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        p = re.compile(r'.+(?<=href \+=)\s*"(.+)"')
        r = p.findall(text)
        res = {}
        for var1 in r[0].split("&"):
            var2 = list(var1.split("="))
            if len(var2) == 1:
                res[var2[0]] = None
            elif len(var2) == 2:
                res[var2[0]] = var2[1]
        assert "err_no" in res
        self.err_no = res["err_no"]
        return self.err_no == "0"

    def request_if_fail(self) -> Optional[str]:
        if self.err_no == "6":
            return "getstyle"


class GetStyleApi(AbstractApi):
    url = "https://passport.baidu.com/viewlog/getstyle"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        self.data = {
            "ak": self.config.store.get("ak", None),
            "tk": self.config.store.get("tk", None),
            "scene": None,
            "isios": 0,
            "type": "default",
            "_": eleven_digits_time(),
            "callback": jquery_random_call_back()
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.verify_image = {
            "url": parse.unquote(m.data["ext"]["img"]),
            "path": None
        }
        return True

    def next(self) -> Optional[str]:
        return "verifyimage"


class VerifyImageApi(AbstractApi):
    url = None
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        self.url = self.config.verify_image["url"]

    async def _after(self, response: ClientResponse) -> bool:
        image_path = f"{IMAGE_PATH}{os.sep}{str(uuid.uuid4())}.jpg"
        with open(image_path, 'wb') as fp:
            fp.write(await response.read())
        self.config.verify_image["path"] = image_path
        return True
