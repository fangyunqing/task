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
        self._api_names = {api.api_name for api in self._apis}

        def _query_seq_pairs(cls, quoter, pairs):
            for key, val in pairs:
                if isinstance(val, (list, tuple)):
                    for v in val:
                        if key in self._api_names:
                            yield quoter(key)
                        else:
                            yield quoter(key) + "=" + quoter(cls._query_var(v))
                else:
                    if key in self._api_names:
                        yield quoter(key)
                    else:
                        yield quoter(key) + "=" + quoter(cls._query_var(val))

        import yarl
        yarl.URL._query_seq_pairs = _query_seq_pairs

    def get_apis(self, task_type: str, api_type: str) -> Dict[str, Type[Api]]:
        apis: Dict[str, Type[Api]] = {}
        for _ in self._apis:
            if task_type in _.task_types and api_type in _.api_types:
                apis[_.api_name] = _
        return apis

