# @Time    : 2023/06/29 14:25
# @Author  : fyq
# @File    : toutiao.py
# @Software: PyCharm

__author__ = 'fyq'


from munch import Munch

from core.task.abstract_task import LoginTask


class TouTiao(LoginTask):
    api_types = ["toutiao"]

    referer = "https://sso.toutiao.com/"

    config = Munch({

    })
