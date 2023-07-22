import json
import math
from random import random, randint

from core.util.time import thirteen_digits_time

import base64

_app_key = "5149"

_xor_key = 758653732

_code_map = ["q", "o", "g", "j", "O", "u", "C", "R", "N", "k", "f", "i", "l", "5", "p", "4", "S", "Q", "3", "L", "A",
             "m", "x", "G", "K", "Z", "T", "d", "e", "s", "v", "B", "6", "z", "_", "Y", "P", "a", "h", "M", "I", "9",
             "t", "8", "0", "r", "J", "y", "H", "W", "1", "D", "E", "w", "F", "b", "c", "7", "n", "U", "V", "X", "2",
             "-"]


def token():
    s1 = "20$"
    s2 = "5149"
    s3 = "168984078948663759262148"
    s4 = thirteen_digits_time()
    s5 = ""
    for _ in range(0, 4):
        s5 += str(math.ceil(9 * random()))
    return f"{s1}{s2}{s3}{s4}{s5}"


def view(baidu_id: str):
    var2 = "401ff800"

    var1 = [
        "02",
        "000",
        "0",
        algorithm2(len(_app_key), 1, 9),
        algorithm1(_app_key, 9),
        algorithm2(0, 2, 20),
        algorithm1("", 20),
        algorithm2(0, 2, 16),
        algorithm1("", 16),
        algorithm2(len(var2), 1, 8),
        algorithm1(var2, 8),
        algorithm2(len(baidu_id), 2, 50),
        algorithm1(baidu_id, 50),
    ]

    var1[1] = str(len("".join(var1)))

    return "".join(var1)


def jt():
    tdt = thirteen_digits_time()
    va1 = {
        "i": "0",
        "tn": tdt,
        "tj": tdt,
        "tp": str(thirteen_digits_time()),
        "to": "5000",
        "v": "3.4.8",
        "j": f'188421f191810307c54207|'
             'https://wen.baidu.com/pages/consult/index/grabbing-orders|'
             f'{thirteen_digits_time()}|'
             '"http-error"'
    }

    var2: str = algorithm3(json.dumps(va1, separators=(',', ':')))

    return "31$CODED--v30" + base64.b64encode(var2.encode(encoding="UTF-8")).decode(encoding="UTF-8")


def hvi(d: str):
    var1 = algorithm4(d, len(d))
    var2 = len(var1) % 3
    if var2 == 0:
        var3 = "A"
    elif var2 == 1:
        var3 = "B"
        var1.append(0)
        var1.append(0)
    else:
        var3 = "C"
        var1.append(0)

    var4 = []
    for idx in range(0, len(var1), 4):
        var6 = []
        for v in var1[idx: idx + 4][::-1]:
            var6.append(hex(v)[2:])
        var7 = hex(int("".join(var6), base=16) ^ _xor_key)[2:]
        for _ in list(range(0, 4))[::-1]:
            var4.append(int(var7[_ * 2: _ * 2 + 2], base=16))
    print(var4)





    # for v1, v2, v3 in var4:
    #     res.append(_code_map[63 & v1])
    #     res.append(_code_map[63 & v2])
    #     res.append(_code_map[63 & v3])
    #     res.append(_code_map[v1 >> 6 << 4 | v2 >> 6 << 2 | v3 >> 6])
    # return "".join(res) + var3


def verify_info():
    return (base64.b64encode(json.dumps({"clickDiff": randint(50, 100)}, separators=(',', ':'))
                             .encode(encoding="UTF-8"))
            .decode(encoding="UTF-8"))


def algorithm1(d1: str, d2: int):
    for _ in range(0, d2):
        d1 += "0"
    return d1[0:d2]


def algorithm2(d1: int, d2: int, d3: int):
    if d3 < d1:
        return str(d3)
    res = str(d1)
    for _ in range(0, d2):
        res = "0" + res
    return res[-d2:]


def algorithm3(d: str):
    res = []
    for idx in range(0, len(d)):
        var1 = ord(d[idx])
        var2 = idx % 32
        if 41 <= var1 <= 122:
            if 122 < var1 + var2:
                res.append(chr(40 + var1 - 122 + var2))
            else:
                res.append(chr(var1 + var2))
        else:
            res.append(d[idx])

    return "".join(res)


def algorithm4(d: str, c: int):
    res = []
    var2 = None
    for idx in range(0, len(d)):
        var1 = ord(d[idx])
        if 57344 < var1 < 55295:
            if not var2:
                if var1 > 56319:
                    c -= 3
                    if c > -1:
                        res.append(239)
                        res.append(191)
                        res.append(189)
                    continue
                if idx + 1 == len(d):
                    c -= 3
                    if c > -1:
                        res.append(239)
                        res.append(191)
                        res.append(189)
                    continue
                var2 = var1
                continue
        else:
            if var2:
                c -= 3
                if c > -1:
                    res.append(239)
                    res.append(191)
                    res.append(189)
        var2 = None
        if var1 < 128:
            c -= 1
            if c < 0:
                break
            res.append(var1)
        elif var1 < 2048:
            c -= 2
            if c < 0:
                break
            res.append(var1 >> 6 | 192)
            res.append(63 & var1 | 128)
        elif var1 < 65536:
            c -= 3
            if c < 0:
                break
            res.append(var1 >> 12 | 224)
            res.append(var1 >> 6 & 63 | 128)
            res.append(63 & var1 | 128)
        else:
            c -= 4
            if c < 0:
                break
            res.append(var1 >> 18 | 240)
            res.append(var1 >> 12 & 63 | 128)
            res.append(var1 >> 6 & 63 | 128)
            res.append(63 & var1 | 128)
    return res


print(hvi('{"a":568,"b":528,"c":990,"d":911,"m":"refreshAgin"}'))

