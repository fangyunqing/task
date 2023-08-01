
# @Time    : 2023/07/26 10:50
# @Author  : fyq
# @File    : cut.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Tuple

from munch import Munch


def cut_rect(w: int, h: int, scale: Tuple[int, int]) -> Munch:
    cut_y = int(w * scale[1] / scale[0])
    cut_x = int(h * scale[0] / scale[1])
    if h > cut_y:
        return Munch({
            "x": 0,
            "y": int((h - cut_y) / 2),
            "w": w,
            "h": cut_y
        })
    else:
        return Munch({
            "x": int((w - cut_x) / 2),
            "y": 0,
            "w": cut_x,
            "h": h
        })
