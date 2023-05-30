# @Time    : 2023/05/29 11:46
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

from pathlib import Path
from typing import List
from .helper import *


def from_google_street(root: Path) -> List[Path]:
    # ignore images with markers (0) and upward views (5)
    paths = [p for p in root.glob('*.jpg') if int(p.stem.rsplit('_')[1]) not in [0, 5]]
    return paths
