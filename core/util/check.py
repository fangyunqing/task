# @Time    : 2023/08/01 9:23
# @Author  : fyq
# @File    : check.py
# @Software: PyCharm

__author__ = 'fyq'


def is_contain_chinese(check_str: str) -> bool:
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def is_all_alpha(check_str: str) -> bool:
    for ch in check_str:
        if not ch.isalpha():
            return False
    return True
