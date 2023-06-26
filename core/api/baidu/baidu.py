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
from json import JSONDecodeError
from typing import Optional, List, Union
from urllib import parse

import aioconsole
from aiohttp import ClientResponse
from munch import Munch

from core import constant
from core.api import InvokeInfo
from core.api.abstract_api import AbstractApi
from core.api.baidu.util import util1, util6, client
from core.api.baidu.util.jsonp import jsonp
from core.util import locus
from core.util import rsa, screen
from core.util.ase import base64_encryption
from core.util.deep_learn import rot_net_captcha
from core.util.format_response import format1
from core.util.random import random_callback, jquery_random_call_back
from core.util.time import thirteen_digits_time

_error = {
    "1": "您输入的帐号格式不正确",
    "2": "用户名或密码有误",
    "3": "验证码不存在或已过期",
    "4": "帐号或密码错误",
    "6": "您输入的验证码有误",
    "7": "用户名或密码有误",
    "16": "您的帐号因安全问题已被限制登录",
    "257": "請輸入驗證碼",
    "120021": "登录失败,请在弹出的窗口操作,或重新登录",
}


class IndexApi(AbstractApi):
    url = "https://www.baidu.com"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        self.config.client = client.random_client()

    async def _after(self, response: ClientResponse) -> bool:
        return True


class GetApiApi(AbstractApi):

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("logincheck")

    url = "https://passport.baidu.com/v2/api/?getapi"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        init_data = {
            "apiType": "login",
            "gid": self.config.gid,
            "loginType": "dialogLogin",
            "loginVersion": "v4",
        }
        sign = "getApiInfo"
        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)

        self.data = jsonp(params=params)
        self.data[constant.kw.callback] = random_callback("bd__cbs__??????")

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        self.config.token = m.data.get("token")
        return True


class GetPublicKeyApi(AbstractApi):
    url = "https://passport.baidu.com/v2/getpublickey"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        init_data = {
            "gid": self.config.gid,
            "loginVersion": "v5",
            "token": self.config.setdefault("token", None)
        }
        sign = "getRsaKey"

        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)

        self.data = jsonp(params=params)
        self.data[constant.kw.callback] = random_callback("bd__cbs__??????")

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

    async def _before(self):
        self.data = {}
        if self.config.store["nameL"]:
            if self.invoke_config.setdefault("image_verify", False):
                model_path = f"{self.task.opt.model_path}{os.sep}rot_net.pth"
                angle = rot_net_captcha(image_path=self.config.verify_image["image_path"],
                                        model_path=model_path,
                                        debug=self.task.opt.debug)
                self.task.info(f"图片旋转角度[{angle}]")
                move_length = round(angle * 212 / 360, 0)
                imitate_points = locus.imitate_locus(client=self.config.client.client,
                                                     component=self.config.client.image_verify,
                                                     move_length=move_length,
                                                     client_point_count=10)
                start_t = thirteen_digits_time()
                point_list = []
                for point in imitate_points.client_points:
                    start_t += random.randint(190, 210)
                    point_list.append({
                        "fx": point.x,
                        "fy": point.y,
                        "t": start_t,
                        "bf": 2
                    })
                min_t = point_list[-1]["t"] + 50
                max_t = point_list[-1]["t"] + 150
                for point in imitate_points.component_points:
                    start_t += random.randint(190, 210)
                    point_list.append({
                        "fx": point.x,
                        "fy": point.y,
                        "t": start_t,
                        "bf": 1
                    })

                data = {
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
                        "clientWidth": self.config.client.client.width,
                        "clientHeight": self.config.client.client.height,
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
                    "ac_c": round(move_length / 212, 2),
                    "backstr": self.config.verify_image["backstr"]

                }
                delay = point_list[-1]["t"] - thirteen_digits_time()
                if delay > 0:
                    await asyncio.sleep(delay / 1000)
                self.data["fs"] = (
                    base64_encryption(data=json.dumps(data),
                                      key=self.config.store.get("nameL", "") + self.config.store.get("nameR", "")))
                self.data["cv"] = "submit"
            else:
                if not self.invoke_config.setdefault("login", True):
                    icp = locus.imitate_client_locus(client=self.config.client.client, point_count=5)
                    start_t = thirteen_digits_time()
                    point_list = []
                    for point in icp.points:
                        start_t += random.randint(190, 210)
                        point_list.append({
                            "fx": point.x,
                            "fy": point.y,
                            "t": start_t,
                            "bf": 2
                        })
                    data = {
                        "cl": [],
                        "mv": point_list,
                        "sc": [],
                        "kb": [],
                        "sb": [],
                        "sd": [],
                        "sm": [],
                        "cr": {
                            "screenTop": 0,
                            "screenLeft": 0,
                            "clientWidth": self.config.client.client.width,
                            "clientHeight": self.config.client.client.height,
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
                        "ac_c": 0,
                    }
                    delay = point_list[-1]["t"] - thirteen_digits_time()
                    if delay > 0:
                        await asyncio.sleep(delay / 1000)
                    self.data["fs"] = (
                        base64_encryption(data=json.dumps(data),
                                          key=self.config.store.get("nameL", "") + self.config.store.get("nameR", "")))
                else:
                    imitate_points = locus.imitate_locus(client=self.config.client.client,
                                                         component=self.config.client.submit,
                                                         move_length=0,
                                                         client_point_count=5)
                    start_t = thirteen_digits_time()
                    point_list = []
                    for point in imitate_points.client_points:
                        start_t += random.randint(190, 210)
                        point_list.append({
                            "fx": point.x,
                            "fy": point.y,
                            "t": start_t,
                            "bf": 2
                        })

                    data = {
                        "cl": [
                            {
                                "x": imitate_points.click_point.x,
                                "y": imitate_points.click_point.y,
                                "t": point_list[-1]["t"] + 100
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
                            "clientWidth": self.config.client.client.width,
                            "clientHeight": self.config.client.client.height,
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
                        "ac_c": 0
                    }
                    delay = point_list[-1]["t"] - thirteen_digits_time() + 100
                    if delay > 0:
                        await asyncio.sleep(delay / 1000)
                    self.data["fs"] = (
                        base64_encryption(data=json.dumps(data),
                                          key=self.config.store.get("nameL", "") + self.config.store.get("nameR", "")))
            self.data["scene"] = self.config.store.get("scene", None)
            self.data["as"] = self.config.store.get("nameL", None)
            self.data["tk"] = self.config.store.get("tk", None)

        self.data[constant.kw.callback] = jquery_random_call_back()
        self.data["ak"] = self.config.store.get("ak", None)
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

    def success(self) -> Optional[InvokeInfo]:
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

    async def _before(self):
        init_data = {
            "token": self.config.token,
            "subpro": "",
            "codeString": "",
            "safeFlag": "0",
            "u": "https://zhidao.baidu.com/",
            "isPhone": "",
            "detect": "1",
            "gid": self.config.gid,
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

        self.data = jsonp(params=params,
                          fuid=init_data["fuid"],
                          trace_id=True)
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
                res[var2[0]] = parse.unquote(var2[1])
        assert "err_no" in res
        self.err_no = res["err_no"]
        if self.err_no in _error:
            self.task.error(_error[self.err_no])
        self.config.login_response = res
        self.config.login_response["traceid"] = self.data["traceid"]
        return self.err_no == "0"

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        return [InvokeInfo("getpublickey"), InvokeInfo("viewlog", Munch({"login": True}))]

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("logininfo")

    def fail(self) -> Optional[InvokeInfo]:
        if self.err_no == "6":
            return InvokeInfo("getstyle", Munch({"action": "send"}))
        elif self.err_no == "120021":
            return InvokeInfo("authwidgetverify", Munch({"action": "send"}))


class GetStyleApi(AbstractApi):
    url = "https://passport.baidu.com/viewlog/getstyle"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
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

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("verifyimage")


class VerifyImageApi(AbstractApi):
    url = None
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        self.url = self.config.verify_image["url"]

    async def _after(self, response: ClientResponse) -> bool:
        image_path = f"{self.task.opt.image_path}{os.sep}{str(uuid.uuid4())}.jpg"
        with open(image_path, 'wb') as fp:
            fp.write(await response.read())
        self.config.verify_image["image_path"] = image_path
        return True

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("viewlog", Munch({"image_verify": True}))


class LoginInfoApi(AbstractApi):
    url = "https://zhidao.baidu.com/api/loginInfo"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]
    is_login: int

    async def _before(self):
        self.data = {
            "t": thirteen_digits_time()
        }

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.read()
        try:
            text_json = json.loads(text)
        except JSONDecodeError:
            self.is_login = 0
        else:
            self.is_login = text_json["isLogin"]
            if self.is_login == 1:
                self.config.login = text_json

        return self.is_login == 1

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        return InvokeInfo("index")

    def fail(self) -> Optional[InvokeInfo]:
        return InvokeInfo("getapi")


class LoginCheckApi(AbstractApi):
    url = "https://passport.baidu.com/v2/api/?logincheck"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        init_data = {
            "token": self.config.token,
            "sub_source": "leadsetpwd",
            "username": self.config.account.username,
            "loginversion": "v4",
            "dv": util6.dv_js_input(),
        }

        sign = "loginCheck"

        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=True)

        self.data = jsonp(params=params,
                          fuid=util6.fuid(self.config),
                          trace_id=True)
        self.data[constant.kw.callback] = random_callback("bd__cbs__??????")

    async def _after(self, response: ClientResponse) -> bool:
        return True

    def success(self) -> Optional[InvokeInfo]:
        return InvokeInfo("login")

    async def pre(self) -> Union[List[InvokeInfo], Optional[InvokeInfo]]:
        return InvokeInfo("viewlog")


class AuthWidgetVerifyApi(AbstractApi):
    url = "https://passport.baidu.com/v2/sapi/authwidgetverify"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    async def _before(self):
        action = self.invoke_config.setdefault("action", "send")

        self.data = {
            "action": action,
            "apiver": "v3",
            "authAction": "",
            "authtoken": self.config.login_response["authtoken"],
            constant.kw.callback: random_callback("bd__pcbs__??????"),
            "countrycode": "",
            "jsonp": 1,
            "lstr": self.config.login_response["lstr"],
            "ltoken": self.config.login_response["ltoken"],
            "needsid": "",
            "questionAndAnswer": "",
            "rsakey": "",
            "subpro": "",
            "tpl": "ik",
            "traceid": self.config.login_response["traceid"],
            "type": "mobile",
            "u": "https://zhidao.baidu.com/",
            "vcode": "",
            "verifychannel": "",
            "winsdk": ""
        }

        if action == "check":
            self.data["secret"] = ""
            self.data["vcode"] = await aioconsole.ainput('请输入验证码:')

    async def _after(self, response: ClientResponse) -> bool:
        text = await response.text()
        m = format1(text, self.data[constant.kw.callback])
        assert m is not None
        if m.errno == "110000":
            return True
        else:
            self.task.debug(m.msg)
            return False

    def success(self) -> Optional[InvokeInfo]:
        if self.data["action"] == "send":
            return InvokeInfo("authwidgetverify", Munch({"action": "check"}))
        else:
            return InvokeInfo("login")

    def fail(self) -> Optional[InvokeInfo]:
        if self.data["action"] == "send":
            pass
        else:
            return InvokeInfo("authwidgetverify", Munch({"action": "send"}))
