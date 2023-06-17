# @Time    : 2023/06/02 13:06
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Optional

from munch import Munch

from core.task.abstract_task import LoginTask, ScheduleTask
from core.util import guid


class BaiduLogin(LoginTask):

    first_api_name = "logininfo"

    api_types = ["baidu"]

    referer = "https://zhidao.baidu.com/"

    config = Munch({
        "gid": guid.guid(),
        "sign1": Munch({
            "getApiInfo": {
                "apiType": "class",
            },
            "login": {
                "isPhone": "isPhone",
                "logLoginType": "logLoginType",
                "memberPass": "mem_pass",
                "safeFlag": "safeflg",
                "timeSpan": "ppui_logintime"
            },
        }),
        "sign2": Munch({
            "login": {
                "memberPass": lambda e: "on" if e else ""
            },
            "loginCheck": {
                "isPhone": lambda e: "true" if e else "false"
            }
        }),
        "store": Munch({
            "nameL": "57a4c3ff",
            "nameR": "appsapi0",
            "ds": "",
            "tk": "",
            "ak": "1e3f2dd1c81f2075171a547893391274",
        }),
        "locus": {

        }
    })


class QuestionScheduleTask(ScheduleTask):

    first_api_name = "homepage"

    api_types = ["question_baidu"]

    login_name = "baidu"

    config = Munch()
