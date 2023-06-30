# @Time    : 2023/06/28 17:19
# @Author  : fyq
# @File    : test_yolo.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
from pytorchyolo import models


class TestYolo(unittest.TestCase):

    def test_yolo(self):
        models.load_model()
