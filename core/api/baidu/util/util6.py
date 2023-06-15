# @Time    : 2023/06/08 14:21
# @Author  : fyq
# @File    : util6.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import math
import random
from typing import List
from urllib import parse

from munch import Munch

from core.util import ase
from core.util.js_displace import left_shift
from core.util.screen import screen, avail_screen
from core.util.time import thirteen_digits_time


def page_token():
    res = str(random.random())
    res = res[0:18]
    while len(res) < 18:
        res += str(int(random.random() * 10))
    return f"tk{res}{thirteen_digits_time()}"


def load_info() -> Munch:
    return Munch({
        "mouseDown": "",
        "keyDown": "",
        "mouseMove": "",
        "version": 26,
        "loadTime": thirteen_digits_time() / 1000,
        "browserInfo": "1,2,101",
        "token": page_token(),
        "location": "https://zhidao.baidu.com/,undefined",
        "screenInfo": "0,0,205,2102,1920,1080,1920,1920,1040",
        "flashInfo": None
    })


def algorithm1(d1, d2):
    """
    function S(e, t) {
            var r = new n(t)
              , o = {
                flashInfo: 0,
                mouseDown: 1,
                keyDown: 2,
                mouseMove: 3,
                version: 4,
                loadTime: 5,
                browserInfo: 6,
                token: 7,
                location: 8,
                screenInfo: 9
            }
              , a = [r.iary([2])];
            for (var i in e) {
                var d = e[i];
                if (void 0 !== d && void 0 !== o[i]) {
                    var c;
                    "number" == typeof d ? (c = d >= 0 ? 1 : 2,
                    d = r.int(d)) : "boolean" == typeof d ? (c = 3,
                    d = r.int(d ? 1 : 0)) : "object" == typeof d && d instanceof Array ? (c = 4,
                    d = r.bary(d)) : (c = 0,
                    d = r.str(d + "")),
                    d && a.push(r.iary([o[i], c, d.length]) + d)
                }
            }
            return a.join("")
        }
    """
    var1 = algorithm5(d2)
    var2 = {
        "flashInfo": 0,
        "mouseDown": 1,
        "keyDown": 2,
        "mouseMove": 3,
        "version": 4,
        "loadTime": 5,
        "browserInfo": 6,
        "token": 7,
        "location": 8,
        "screenInfo": 9
    }
    var3 = [_iary([2], var1.get("dict2"))]
    for key in d1:
        var4 = d1[key]
        if var4 is not None and key in var2:
            if isinstance(var4, int) or isinstance(var4, float):
                if var4 >= 0:
                    var5 = 1
                else:
                    var5 = 2
                var4 = _int(var4, var1.get("dict"))
            elif isinstance(var4, bool):
                var5 = 3
                var4 = _int(1 if var4 else 0, var1.get("dict"))
            elif isinstance(var4, list):
                var5 = 4
                var4 = _bary(var4, var1.get("dict"))
            else:
                var5 = 0
                var4 = _str(str(var4), var1.get("dict"))
            if var4:
                var3.append(_iary([var2[key], var5, len(var4)], var1.get("dict2")) + var4)
    return "".join(var3)


def algorithm2(data: List[List]):
    """
    function o(e) {
        for (var t = [], n = 0; n < e.length; n++)
            for (var r = e[n][0]; r <= e[n][1]; r++)
                t.push(String.fromCharCode(r));
        return t
    }
    """
    res = []
    for index in range(0, len(data)):
        var1 = data[index][0]
        var2 = data[index][1]
        for var3 in range(var1, var2 + 1):
            res.append(chr(var3))
    return res


def algorithm3(e, t):
    """
    function a(e, t) {
        var n = ""
          , r = Math.abs(parseInt(e));
        if (r)
            for (; r; )
                n += t[r % t.length],
                r = parseInt(r / t.length);
        else
            n = t[0];
        return n
    }
    """
    res = ""
    var1 = abs(int(e))
    if var1:
        while var1 != 0:
            res += t[var1 % len(t)]
            var1 = int(var1 / len(t))
    else:
        res = t[0]
    return res


def algorithm4(d1, d2: str):
    """
    function r(e, t) {
        for (var n = t.split(""), r = 0; r < e.length; r++) {
            var o = r % n.length;
            o = n[o].charCodeAt(0),
            o %= e.length;
            var a = e[r];
            e[r] = e[o],
            e[o] = a
        }
        return e
    }
    """
    var1 = d2
    for index in range(0, len(d1)):
        var2 = index % len(var1)
        var2 = ord(var1[var2][0])
        var2 %= len(d1)
        var3 = d1[index]
        d1[index] = d1[var2]
        d1[var2] = var3
    return d1


def algorithm5(data):
    """
    function n(e) {
        var t = [[48, 57], [65, 90], [97, 122], [45, 45], [126, 126]]
          , n = o(t)
          , a = o(t.slice(1));
        e && (n = r(n, e),
        a = r(a, e)),
        this.dict = n,
        this.dict2 = a
    }
    """
    var1 = [[48, 57], [65, 90], [97, 122], [45, 45], [126, 126]]
    var2 = algorithm2(var1)
    var3 = algorithm2(var1[1:])
    var2 = algorithm4(var2, data)
    var3 = algorithm4(var3, data)
    res = {
        "dict": var2,
        "dict2": var3
    }
    return res


def _int(d1, d2):
    """
    "int": function(e) {
        return a(e, this.dict)
    },
    """
    return algorithm3(d1, d2)


def _iary(d1, d2):
    """
    iary: function(e) {
        for (var t = "", n = 0; n < e.length; n++) {
            var r = a(e[n], this.dict2);
            t += r.length > 1 ? r.length - 2 + r : r
        }
        return t
    },
    """
    res = ""
    for index in range(0, len(d1)):
        var1 = algorithm3(d1[index], d2)
        res += len(var1) - 2 + var1 if len(var1) > 1 else var1
    return res


def _bary(d1, d2):
    """
    bary: function(e) {
        for (var t = 0, n = {}, r = 0; r < e.length; r++)
            e[r] > t && (t = e[r],
            n[e[r]] = !0);
        var o = parseInt(t / 6);
        o += t % 6 ? 1 : 0;
        for (var a = "", r = 0; o > r; r++) {
            for (var i = 6 * r, d = 0, c = 0; 6 > c; c++)
                n[i] && (d += Math.pow(2, c)),
                i++;
            a += this.dict[d]
        }
        return a
    },
    """
    var1 = 0
    var2 = {}
    for index in range(0, len(d1)):
        if d1[index] > var1:
            var1 = d1[index]
            var2[d1[index]] = True
    var3 = int(var1 / 6)
    var3 += 1 if var1 % 6 else 0
    res = ""
    for index in range(0, var3):
        var4 = 6 * index
        var5 = 0
        for c in range(0, 6):
            if var2[var4]:
                var5 += math.pow(2, c)
            var4 += 1
        res += d2[var5]
    return res


def _str(d1, d2):
    """
    str: function(e) {
        for (var t = [], n = 0; n < e.length; n++) {
            var r = e.charCodeAt(n);
            r >= 1 && 127 >= r ? t.push(r) : r > 2047 ? (t.push(224 | r >> 12 & 15),
            t.push(128 | r >> 6 & 63),
            t.push(128 | r >> 0 & 63)) : (t.push(192 | r >> 6 & 31),
            t.push(128 | r >> 0 & 63))
        }
        for (var o = "", n = 0, a = t.length; a > n; ) {
            var i = t[n++];
            if (n >= a) {
                o += this.dict[i >> 2],
                o += this.dict[(3 & i) << 4],
                o += "__";
                break
            }
            var d = t[n++];
            if (n >= a) {
                o += this.dict[i >> 2],
                o += this.dict[(3 & i) << 4 | (240 & d) >> 4],
                o += this.dict[(15 & d) << 2],
                o += "_";
                break
            }
            var c = t[n++];
            o += this.dict[i >> 2],
            o += this.dict[(3 & i) << 4 | (240 & d) >> 4],
            o += this.dict[(15 & d) << 2 | (192 & c) >> 6],
            o += this.dict[63 & c]
        }
        return o
    }
    """
    var1 = []
    for index in range(0, len(d1)):
        var2 = ord(d1[index])
        if 1 <= var2 <= 127:
            var1.append(var2)
        elif var2 > 2047:
            var1.append(224 | var2 >> 12 & 15)
            var1.append(128 | var2 >> 6 & 63)
            var1.append(128 | var2 >> 0 & 63)
        else:
            var1.append(192 | var2 >> 6 & 31)
            var1.append(128 | var2 >> 0 & 63)
    res = ""
    index = 0
    var3 = len(var1)
    while var3 > index:
        var4 = var1[index]
        index += 1
        if index >= var3:
            res += d2[var4 >> 2]
            res += d2[left_shift(3 & var4, 4)]
            res += "__"
            break

        var5 = var1[index]
        index += 1
        if index >= var3:
            res += d2[var4 >> 2]
            res += d2[left_shift(3 & var4, 4) | (240 & var5) >> 4]
            res += d2[left_shift(15 & var5, 2)]
            res += "_"
            break

        var6 = var1[index]
        index += 1
        res += d2[var4 >> 2]
        res += d2[left_shift(3 & var4, 4) | (240 & var5) >> 4]
        res += d2[left_shift(15 & var5, 2) | (192 & var6) >> 6]
        res += d2[63 & var6]
    return res


def dv_js_input():
    li = load_info()
    return f"{li.token}@{algorithm1(li, li.token)}"


def fuid(config: Munch):
    data = {
        "userAgent": parse.quote(config.user_agent, safe="()"),
        "canvas": "1f36b789fc126e9eda29f85b38587e11",
        "language": "zh-CN",
        "colorDepth": "24",
        "deviceMemory": "8",
        "hardwareConcurrency": "6",
        "screenResolution": parse.quote(",".join([str(s) for s in screen()])),
        "availableScreenResolution": parse.quote(",".join([str(s) for s in reversed(avail_screen())])),
        "timezoneOffset": "-480",
        "timezone": "",
        "sessionStorage": "true",
        "localStorage": "true",
        "indexedDb": "true",
        "addBehavior": "false",
        "openDatabase": "true",
        "cpuClass": "",
        "platform": "Win32",
        "plugins": "undefined",
        "webgl": "9d4c9da84cfcaf6a39079d6bfa494192",
        "webglVendorAndRenderer": "",
        "adBlock": "false",
        "hasLiedLanguages": "false",
        "hasLiedResolution": "false",
        "hasLiedOs": "false",
        "hasLiedBrowser": "false",
        "touchSupport": parse.quote("0,false,false"),
        "fonts": "49",
        "audio": "undefined"
    }

    return ase.base64_encryption(json.dumps(data, separators=(',', ':'), ensure_ascii=False), "FfdsnvsootJmvNfl")


if __name__ == "__main__":
    print(fuid(Munch({"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/112.0.0.0 Safari/537.36"})))
