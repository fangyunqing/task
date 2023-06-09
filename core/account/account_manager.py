# @Time    : 2023/06/06 15:05
# @Author  : fyq
# @File    : account_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from dataclasses import dataclass
from functools import cache
from typing import List

import yaml
from munch import Munch


@dataclass
class Account:

    username: str

    password: str


class AccountManager:

    def __init__(self, opt: Munch):
        self._opt = opt
        try:
            with open(self._opt.account, 'r', encoding='utf-8') as f:
                self._datas = yaml.load(stream=f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            self._datas = []

    @cache
    def get_account(self, task_type: str) -> List[Account]:
        accounts: List[Account] = []
        for data in self._datas:
            if task_type == data.get("type"):
                accounts.append(Account(username=data.get("username"),
                                        password=data.get("password")))
        return accounts
