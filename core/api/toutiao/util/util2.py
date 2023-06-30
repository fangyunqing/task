# @Time    : 2023/06/29 16:24
# @Author  : fyq
# @File    : util2.py
# @Software: PyCharm

__author__ = 'fyq'

import copy
from typing import Dict, List

from core.api.toutiao.util import util1


def algorithm1(d1: Dict, d2: List):
    """
    function(e, t) {
        var n, o = 0, r = 0;
        if ("object" != typeof e)
            return e;
        if (!t || t.length <= 0)
            return e;
        for (var a = d({
            mix_mode: o
        }, e), i = 0, s = t.length; i < s; ++i)
            void 0 !== (n = a[t[i]]) && (o |= 1,
            r |= 1,
            a[t[i]] = T(n));
        return a.mix_mode = o,
        a.fixed_mix_mode = r,
        a
    }
    :param d1:
    :param d2:
    :return:
    """

    if not d2 or not d1:
        return d1

    var1 = copy.copy(d1)
    var2 = 0
    var3 = 0
    var1["mix_mode"] = var2
    for s in d2:
        if s in d1 and d1[s]:
            var2 |= 1
            var3 |= 1
            var1[s] = util1.algorithm1(d1[s])
    var1["mix_mode"] = var2
    var1["fixed_mix_mode"] = var3

    return var1


if __name__ == "__main__":
    e = {
        "mobile": "+86 18750767178",
        "type": 24,
        "is6Digits": 1
    }
    t = [
        "mobile",
        "type"
    ]
    print(algorithm1(e, t))
