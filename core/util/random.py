# @Time    : 2023/06/03 15:20
# @Author  : fyq
# @File    : random.py
# @Software: PyCharm

__author__ = 'fyq'

import random
import string

from core.util.time import thirteen_digits_time


def random_callback(rule="??__???__??????"):
    res = ""
    for index, r in enumerate(rule):
        if r == "?":
            res += random.choice(string.ascii_lowercase + string.digits)
        else:
            res += r
    return res


def jquery_random_call_back():
    """
    jQuery110207053490627294874_1680752947519
    """
    res = "jQuery"
    for n in range(0, 21):
        res += str(int(random.random() * 10))
    res += f"_{thirteen_digits_time()}"

    return res


def random_trace_id():
    res = ""
    for _ in range(6):
        res += random.choice(string.ascii_uppercase + string.digits)
    return res + "01"
