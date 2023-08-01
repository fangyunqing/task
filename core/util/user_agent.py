# @Time    : 2023/05/30 16:13
# @Author  : fyq
# @File    : user_agent.py
# @Software: PyCharm

__author__ = 'fyq'

__all__ = ["random_ua"]

import random

_ua = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
]


def random_ua() -> str:
    return random.choice(_ua)
