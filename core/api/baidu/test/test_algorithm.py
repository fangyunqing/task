# @Time    : 2023/06/05 15:49
# @Author  : fyq
# @File    : test_algorithm.py
# @Software: PyCharm

__author__ = 'fyq'

import time
import unittest

from core.api.baidu.util import util2, util4, util5
from core.util.ase import encryption


class TestAlgorithm(unittest.TestCase):

    def test_algorithm1(self):
        var2 = 1685952504705
        var3 = var2
        while True:
            var3 = util2.algorithm6(
                util2.algorithm2(
                    util2.algorithm1(
                        util4.algorithm14(var3, None, None)
                    )
                )
            )
            if str(var3)[0: 2] == "00":
                break
        print(var3)

    def test_algorithm2(self):
        var1 = (
                   {'token': '',
                    'tpl': 'ik',
                    'subpro': '',
                    'apiver': 'v3',
                    'tt': 1685952770088,
                    'class': 'login',
                    'gid': '92AC2EC-6816-4174-91FA-4C309DE0F0BAA',
                    'logintype': 'dialogLogin',
                    'loginversion': 'v4',
                    'alg': 'v3',
                    'time': 1685952770}
        )
        d3 = "moonshad0moonsh1"
        print(encryption(util5.add_screen(var1, None), d3))
