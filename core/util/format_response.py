# @Time    : 2023/06/06 13:27
# @Author  : fyq
# @File    : format_response.py
# @Software: PyCharm

__author__ = 'fyq'

import json
from json.decoder import JSONDecodeError

from loguru import logger
from munch import Munch
from typing import Optional


def format1(text: str, callback: str) -> Optional[Munch]:
    try:
        return Munch(json.loads(text.replace(callback, "").replace(")", "").replace("(", "").replace("'", '"')))
    except JSONDecodeError:
        logger.warning(f"{text} format1 fail")