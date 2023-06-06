# @Time    : 2023/06/03 15:20
# @Author  : fyq
# @File    : callback.py
# @Software: PyCharm

__author__ = 'fyq'

import random
import string


def random_callback(rule="??__???__??????"):
    res = ""
    for index, r in enumerate(rule):
        if r == "?":
            if index in [0, 1] or random.randint(0, 1) == 0:
                res += random.choice(string.ascii_lowercase)
            else:
                res += str(int(random.random() * 10))
        else:
            res += r
    return res
