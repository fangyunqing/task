# @Time    : 2023/06/03 9:32
# @Author  : fyq
# @File    : guid.py
# @Software: PyCharm

__author__ = 'fyq'

import uuid


def guid():
    """
        eg "39659EE-212C-48BB-9FE6-9CE756F3E2B6"
    :return:
    """
    s = str(uuid.uuid4()).upper()
    return s[1: len(s)]


def guid32():
    return str(uuid.uuid1()).replace("-", "")
