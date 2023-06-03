# @Time    : 2023/06/02 13:59
# @Author  : fyq
# @File    : baidu.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Tuple, Optional, Dict

from aiohttp import ClientResponse

from core import constant
from core.api.abstract_api import AbstractApi
from core.task import Task

from core.util import guid
from core.api.baidu.util import util1


class IndexApi(AbstractApi):
    url = "https://www.baidu.com"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def __init__(self, task: Task):
        super(IndexApi, self).__init__(task)

    def _before(self):
        pass

    def _after(self, response: ClientResponse) -> Tuple[bool, Optional[Dict]]:
        pass


class GetApiApi(AbstractApi):
    url = "https://passport.baidu.com/v2/api/?getapi"
    method = constant.hm.get
    api_types = ['baidu']
    task_types = [constant.kw.login]

    def _before(self):
        init_data = {
            "apiType": "login",
            "gid": guid.guid(),
            "loginType": "dialogLogin",
            "loginVersion": "v4",
        }
        sign = "getApiInfo"
        params = util1.add_params(init_data=init_data,
                                  sign=sign,
                                  d1=self.config.sign1.get(sign),
                                  d2=self.config.sign2.get(sign),
                                  static=False)
        process = {
            "charset": "utf-8",
            "processData": ""
        }


    def _after(self, response: ClientResponse) -> Tuple[bool, Optional[Dict]]:
        pass
