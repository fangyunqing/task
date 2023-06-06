# @Time    : 2023/06/03 15:27
# @Author  : fyq
# @File    : test_app.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest

from core import app


class TestApp(unittest.TestCase):

    def test_app(self):
        app.run_login("baidu")
