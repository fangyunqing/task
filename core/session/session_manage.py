# @Time    : 2023/05/31 16:09
# @Author  : fyq
# @File    : session_manage.py
# @Software: PyCharm

__author__ = 'fyq'

from dataclasses import dataclass

from aiohttp import ClientSession
from typing import Optional, Dict
import asyncio


@dataclass
class SessionStatus:
    """
        会话状态
    """

    """
        会话实例
    """
    session: Optional[ClientSession] = None

    """
        会话事件
    """
    event: asyncio.Event = asyncio.Event()


class SessionManage:

    def __init__(self):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass
