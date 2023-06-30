# @Time    : 2023/06/24 15:13
# @Author  : fyq
# @File    : test_re.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
import pyparsing as pp


class TestRe(unittest.TestCase):

    def test_one(self):
        s = ('<div class="line content">'
             '<div id="answer-content-4420309342" accuse="aContent" class="answer-text line">'
             '<div class="wgt-myanswer-mask">'
             '<div class="wgt-myanswer-showbtn">')

        u = (
                pp.Literal("answer-content-") + pp.Word(pp.nums, exact=10)
        )

        datas = []
        urls = []
        idx = 0
        for x, b, e in u.scan_string(s):
            print(s[b:e])
        print(urls)
        print(datas)
