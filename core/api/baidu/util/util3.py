# @Time    : 2023/06/03 13:42
# @Author  : fyq
# @File    : util3.py
# @Software: PyCharm

__author__ = 'fyq'

import time

from core.api.baidu.util import util2, util4, util5
from core.util.ase import encryption

_version = {
    "version": "v3"
}

moonshadV3 = {
    "OOOO00": lambda t, r: encrypt(t, r, "moonshad5moonsh2"),
    "OOO00O": lambda t, r: encrypt(t, r, "moonshad3moonsh0"),
    "OOO000": lambda t, r: encrypt(t, r, "moonshad8moonsh6"),
    "OOO0OO": lambda t, r: encrypt(t, r, "moonshad0moonsh1"),
    "O0OOO0": lambda t, r: encrypt(t, r, "moonshad1moonsh9")
}


def encrypt(d1, d2, d3):
    """
        function c(t, r, e) {
            if (!window.screen.width || !window.screen.height)
                return {};
            var n = {};
            try {
                var i = f(t || {});
                i.alg = h.version,
                i.time = Math.round((new Date).getTime() / 1e3),
                i.hasOwnProperty("sig") && delete i.sig,
                i.hasOwnProperty("traceid") && delete i.traceid,
                i.hasOwnProperty("callback") && delete i.callback,
                i.hasOwnProperty("elapsed") && delete i.elapsed,
                i.hasOwnProperty("shaOne") && delete i.shaOne;
                var o, a = "";
                for (o = a = (new Date).getTime(); "00" !== (a = l(d(a))).toString().substr(0, 2); )
                    ;
                if (n = {
                    time: i.time,
                    alg: i.alg,
                    sig: h.encryption(i, r, e),
                    elapsed: (new Date).getTime() - o || "",
                    shaOne: a
                },
                window.passFingerPrint) {
                    var s = window.passFingerPrint();
                    n.rinfo = p({
                        fuid: d(s.fuid)
                    })
                }
            } catch (c) {
                u(c)
            }
            return n
        }
    """
    var1 = {k: v for k, v in d1.items()}
    var1["alg"] = _version["version"]
    var1["time"] = round(time.time())
    var1.pop("sig", "")
    var1.pop("traceid", "")
    var1.pop("callback", "")
    var1.pop("elapsed", "")
    var1.pop("shaOne", "")
    var2 = int(time.time() * 1000)
    var3 = var2
    while True:
        var3 = util2.algorithm6(
            util2.algorithm2(
                util2.algorithm1(
                    util4.algorithm14(var3, None, None)
                )
            )
        )
        if str(var3)[0: 2] == "00":
            break

    n = {
        "time": var1["time"],
        "alg": var1["alg"],
        "sig": encryption(util5.add_screen(var1, None), d3),
        "elapsed": int(time.time() * 1000) - var2,
        "shaOne": var3
    }

    return n
