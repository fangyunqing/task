# @Time    : 2023/06/02 13:59
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

import asyncio
import json
import os
import random
import re
import uuid
from typing import Optional
from urllib import parse

from aiohttp import ClientResponse
from munch import Munch

from core import constant
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import util1, util6, locus
from core.api.baidu.util.jsonp import jsonp
from core.util import guid, rsa, screen
from core.util.ase import base64_encryption
from core.util.callback import random_callback, jquery_random_call_back
from core.util.deep_learn import rot_net_captcha
from core.util.format_response import format1
from core.util.time import thirteen_digits_time
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

    def next(self) -> Optional[InvokeInfo]:
        return InvokeInfo("getpublickey")

    def pre(self) -> Optional[InvokeInfo]:
        return InvokeInfo("index")

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

    def next(self) -> Optional[InvokeInfo]:
        return InvokeInfo("login")

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
    op = None

    def _before(self):
        self.data = {constant.kw.callback: jquery_random_call_back(),
                     "ak": self.config.store.get("ak", None),
                     "as": self.config.store.get("nameL", None)}

        if self.config.locus:
            self.task.debug("\n" + "模拟轨迹:" + json.dumps(self.config.locus, indent="   "))
            self.data["fs"] = (
                base64_encryption(data=json.dumps(self.config.locus),
                                  key=self.config.store.get("nameL", "") + self.config.store.get("nameR", "")))
            if "cv" in self.invoke_config:
                if self.invoke_config.cv:
                    self.data["cv"] = "submit"
            else:
                self.data["cv"] = "submit"
        else:
            self.data["fs"] = None

        self.data["tk"] = self.config.store.get("tk", None)
        self.data["scene"] = self.config.store.get("scene", None)
        self.data["_"] = thirteen_digits_time()

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.store["ds"] = m.data.get("ds", "")
        self.config.store["as"] = m.data.get("as", "")
        self.config.store["tk"] = m.data.get("tk", "")
        self.config.store["nameL"] = m.data.get("as", "6bffae1c")
        if "op" in m.data:
            self.op = m.data["op"]
        else:
            self.op = None
        return True

    def next(self) -> Optional[InvokeInfo]:
        if self.op in [0, 2]:
            return InvokeInfo("getstyle")
        elif self.op == 1:
            return InvokeInfo("login")


class LoginApi(AbstractApi):
    url = "https://passport.baidu.com/v2/api/?login"
    method = constant.hm.post_data
    api_types = ['baidu']
    task_types = [constant.kw.login]
    err_no = None

    def pre(self) -> Optional[InvokeInfo]:
        return InvokeInfo("viewlog", Munch({"cv": False}))

    def _before(self):
        init_data = {
            "token": self.config.token,
            "subpro": "",
            "codeString": "",
            "safeFlag": "0",
            "u": "https://zhidao.baidu.com/",
            "isPhone": "",
            "detect": "1",
            "gid": guid.guid(),
            "quick_user": "0",
            "logintype": "dialogLogin",
            "logLoginType": "pc_loginDialog",
            "idc": "",
            "loginMerge": "true",
            "mkey": "",
            "splogin": "rate",
            "userName": self.config.account.username,
            "password": rsa.encryption(self.config.pubkey, self.config.account.password),
            "memberPass": "on",
            "rsaKey": self.config.key,
            "crypttype": 12,
            "timeSpan": random.randint(200, 4000),
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
                                  static=True)
        process = {
            "charset": "utf-8",
            "processData": ""
        }

        self.data = jsonp(params=params, process=process, fuid=init_data["fuid"])
        self.data[constant.kw.callback] = "parent." + random_callback("bd__pcbs__??????")

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

    def request_if_fail(self) -> Optional[InvokeInfo]:
        if self.err_no == "6":
            return InvokeInfo("getstyle")


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
            "_": thirteen_digits_time(),
            "callback": jquery_random_call_back()
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.verify_image = {
            "url": parse.unquote(m.data["ext"]["img"]),
            "backstr": m.data["backstr"]
        }
        return True

    def next(self) -> Optional[InvokeInfo]:
        return InvokeInfo("verifyimage")


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
        # pytorch计算出图片旋转的角度
        model_path = f"{self.task.opt.model_path}{os.sep}rot_net.pth"
        angle = rot_net_captcha(image_path=image_path,
                                model_path=model_path,
                                debug=self.task.opt.debug)
        self.task.info(f"图片旋转角度[{angle}]")
        angel_length = round(angle * 212 / 360, 0)
        # 模拟滑动轨迹
        imitate_points = locus.imitate_locus(25, 212, angel_length)
        start_t = thirteen_digits_time()
        point_list = []
        for point in imitate_points.error_points:
            start_t += random.randint(190, 210)
            point_list.append({
                "fx": point.x,
                "fy": point.y,
                "t": start_t,
                "bf": 2
            })
        min_t = point_list[-1]["t"] + 50
        max_t = point_list[-1]["t"] + 150
        for point in imitate_points.right_points:
            start_t += random.randint(190, 210)
            point_list.append({
                "fx": point.x,
                "fy": point.y,
                "t": start_t,
                "bf": 1
            })

        self.config.locus = {
            "cl": [
                {
                    "x": imitate_points.click_point.x,
                    "y": imitate_points.click_point.y,
                    "t": random.randint(min_t, max_t)
                }
            ],
            "mv": point_list,
            "sc": [],
            "kb": [],
            "sb": [],
            "sd": [],
            "sm": [],
            "cr": {
                "screenTop": 0,
                "screenLeft": 0,
                "clientWidth": imitate_points.client_width,
                "clientHeight": imitate_points.client_height,
                "screenWidth": screen.screen()[0],
                "screenHeight": screen.screen()[1],
                "availWidth": screen.avail_screen()[0],
                "availHeight": screen.avail_screen()[1],
                "outerWidth": screen.outer_screen()[0],
                "outerHeight": screen.outer_screen()[1],
                "scrollWidth": screen.scroll_screen()[0],
                "scrollHeight": screen.scroll_screen()[1]
            },
            "simu": 0,
            "ac_c": round(angel_length / 212, 2),
            "backstr": self.config.verify_image["backstr"]

        }
        delay = point_list[-1]["t"] - thirteen_digits_time()
        if delay > 0:
            await asyncio.sleep(delay / 1000)
        return True

    def next(self) -> Optional[InvokeInfo]:
        return InvokeInfo("viewlog")
