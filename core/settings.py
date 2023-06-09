# @Time    : 2023/06/06 15:18
# @Author  : fyq
# @File    : settings.py
# @Software: PyCharm

__author__ = 'fyq'

import os

default_opt = {
    "debug": True,
    "proxy": None,
    "account": f"core{os.sep}account.yml",
    "response_len": 10240,
    "image_path": f"image",
    "model_path": f"model",
    "sleep_time": 2,
    "cookies_path": f"core{os.sep}cookies",
    "ua_path": f"core{os.sep}ua"
}
