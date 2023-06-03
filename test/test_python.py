# @Time    : 2023/06/01 9:17
# @Author  : fyq
# @File    : test_python.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
from functools import wraps
from typing import List, Union


class TestPython(unittest.TestCase):

    def test_init_subclass(self):
        class A:
            def __init_subclass__(cls, **kwargs):
                print(cls.__name__)

        class B(A):
            pass

        class C(B):
            pass

    def test_decorator(self):

        def add_api(api_type: Union[List, str]):
            def add_api_decorator(cls):
                print(cls.__name__)
                cls.abc = "33"
                return cls
            return add_api_decorator

        @add_api(api_type="Login")
        class A:
            pass

        print(A.__dict__)