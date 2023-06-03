# @Time    : 2023/06/02 13:06
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Optional

from munch import Munch

from core.task.abstract_task import LoginTask


class BaiduLogin(LoginTask):
    api_types = ["baidu"]

    config = Munch({
        "sign1": Munch({
            "getApiInfo": {
                "apiType": "class",
            },
        }),
        "sign2": Munch({
            "login": {
                "memberPass": lambda e: "on" if e else ""
            },
            "loginCheck": {
                "isPhone": lambda e: "true" if e else "false"
            }
        })
    })

    def __init__(self, opt: Optional[Munch]):
        super(BaiduLogin, self).__init__(opt=opt)
