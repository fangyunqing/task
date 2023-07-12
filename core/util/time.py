# @Time    : 2023/06/08 13:56
# @Author  : fyq
# @File    : time.py
# @Software: PyCharm

__author__ = 'fyq'

import datetime
import time


def thirteen_digits_time():
    """
    1686203781424
    :return:
    """
    return int(time.time() * 1000)


def get_date():
    """
        2023-07-06
    :return:
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")
