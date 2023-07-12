# @Time    : 2023/06/02 13:06
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

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
            "nameL": "",
            "nameR": "appsapi0",
            "ds": "",
            "tk": "",
            "ak": "1e3f2dd1c81f2075171a547893391274",
        }),
        "locus": {

        }
    })


class QuestionScheduleTask(ScheduleTask):

    first_api_name = "choice"

    api_types = ["question_baidu"]

    login_name = "baidu"

    config = Munch({
        "task_sign": True,
        "like": True,
        "comment": True
    })

    repeat_time = 90


class ArticleScheduleTask(ScheduleTask):

    first_api_name = "article"

    api_types = ["article_baidu"]

    login_name = "baidu"

    config = Munch()

    start_hour = 9

    repeat_time = 600
