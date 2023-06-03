# @Time    : 2023/06/01 13:10
# @Author  : fyq
# @File    : api_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Type, List, Dict

from core.api import Api
from core.api.api import api_cls_list


class ApiManager:

    def __init__(self):
        self._apis: List[Type[Api]] = api_cls_list

    def get_apis(self, task_type: str, api_type: str) -> Dict[str, Type[Api]]:
        apis: Dict[str, Type[Api]] = {}
        for _ in self._apis:
            if task_type in _.task_types and api_type in _.api_types:
                apis[_.api_name] = _
        return apis

