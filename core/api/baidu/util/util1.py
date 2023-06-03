# @Time    : 2023/06/03 10:17
# @Author  : fyq
# @File    : util1.py
# @Software: PyCharm

__author__ = 'fyq'

import time
from typing import Dict, Any
from urllib.parse import unquote

_static = {
    "charset": "GBK",
    "product": "ik",
    "staticPage": "https://zhidao.baidu.com/static/common/https-html/v3Jump.html",
    "subpro": "",
    "token": ""
}

_check = {
    "checkPassword": {
        "fromreg": 1
    },
    "reg": {
        "registerType": 1,
        "verifypass": lambda e: e["password"] if "password" in e else None
    }
}

_password = {
    "password": True
}


def add_params(init_data: Dict[str, Any],
               sign: str,
               d1: Dict[str, Any],
               d2: Dict[str, Any],
               static: bool) -> Dict[str, Any]:
    """
        function i(e, t, n, i, s) {
            var o = s ? {
                staticpage: _.staticPage,
                charset: _.charset || document.characterSet || document.charset || ""
            } : {}
              , a = f[t];
            if (a)
                for (var r in a) {
                    if (a.hasOwnProperty(r)) {
                        var l = a[r];
                        o[r] = "function" == typeof l ? l(e) : l
                    }
                    "verifypass" == r && (o[r] = decodeURIComponent(o[r]))
                }
            if (o.token = _.token || "",
            o.tpl = _.product || "",
            o.subpro = _.subpro || "",
            o.apiver = "v3",
            o.tt = (new Date).getTime(),
            e) {
                n = n || {},
                i = i || {};
                for (var r in e)
                    if (e.hasOwnProperty(r)) {
                        var d = i[r]
                          , u = d ? d(e[r], e) : e[r];
                        "string" == typeof u && (s && (u = decodeURIComponent(u)),
                        h[r] || (u = c.trim(u))),
                        o[n[r] || r.toLowerCase()] = u
                    }
            }
            return o
        }
    :param init_data: e
    :param sign: t
    :param d1: n
    :param d2: i
    :param static: s
    :return:
    """
    if static:
        params = {
            "staticpage": _static["staticPage"],
            "charset": _static["charset"]
        }
    else:
        params = {}

    if sign in _check:
        for key, val in _check[sign].items():
            if callable(val):
                params[key] = val(init_data)
                if key == "verifypass":
                    params[key] = unquote(params[key])

    params["token"] = _static["token"]
    params["tpl"] = _static["product"]
    params["subpro"] = _static["subpro"]
    params["apiver"] = "v3"
    params["tt"] = int(time.time() * 1000)
    if init_data:
        d1 = d1 if d1 else {}
        d2 = d2 if d2 else {}
        for key, val in init_data.items():
            if key in d2:
                u = d2[key](key)
            else:
                u = val

            if isinstance(val, str) and static:
                u = unquote(u)

            if key in d1:
                params[d1[key]] = u
            else:
                params[key.lower()] = u

    return params
