# @Time    : 2023/06/16 16:31
# @Author  : fyq
# @File    : utdata.py
# @Software: PyCharm

__author__ = 'fyq'

import random
from typing import List

from core.util.screen import screen
from core.util.time import thirteen_digits_time


def utdata(t1: int, t2: int):
    """
    function c() {
        if (p)
            return g;
        m.each(v.ea, function(t, e) {
            v.ea[t] = j[e]
        });
        var t = [u(), r(), (new Date).getTime() - d, [screen.width, screen.height].join(",")].join("	");
        return g.c = s(t) + "," + l + w,
        p = !0,
        g
    }
    :return:
    """
    ea = []
    for _ in range(random.randint(5, 50)):
        ea.append(random.randint(0, 4))
    data = "\t".join([
        ",",
        algorithm1(ea),
        str(thirteen_digits_time() - t1),
        ",".join([str(s) for s in screen()])
    ])

    return f"{data},{t2}1"


def algorithm1(data: List[int]) -> str:
    """
    function r() {
        var t = v.ea.concat()
          , e = t.length;
        return e > 10 && (t = t.splice(e - 10, 10)),
        t.join(",")
    }
    :param data: 
    :return: 
    """

    res = "".join([str(d) for d in data])
    if len(res) > 10:
        res = res[-10:]
    return ",".join(res)


if __name__ == "__main__":
    print(utdata(thirteen_digits_time(), thirteen_digits_time()))
