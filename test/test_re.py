# @Time    : 2023/06/24 15:13
# @Author  : fyq
# @File    : test_re.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
import pyparsing as pp


class TestRe(unittest.TestCase):

    def test_one(self):
        s = ('# 迎接新春，迎接幸福\n\n![春节](https://source.unsplash.com/960x640/?spring)\n\n'
             '春节是中国最重要的传统节日之一，也是全球华人共同庆祝的节日。每年农历正月初一，人们会在这一天欢聚一堂，共度团圆时光。\n\n![团圆]('
             'https://source.unsplash.com/960x640/?reunion)\n\n'
             '春节期间，人们会进行各种各样的活动，如贴春联、挂灯笼、放鞭炮等。这些活动都寓意着希望新的一年能够平安、幸福、顺利。\n\n![灯笼]('
             'https://source.unsplash.com/960x640/?lantern)\n\n'
             '除了传统的活动，现代化的庆祝方式也越来越受到欢迎。例如，人们会在社交媒体上分享自己的春节照片，或者通过视频通话与远在他乡的亲友团聚。\n\n![视频通话]('
             'https://source.unsplash.com/960x640/?video)\n\n无论是传统还是现代，春节都是一个充满欢乐和祝福的节日。让我们一起迎接新春，迎接幸福！(https://source.unsplash.com/960x640/?video)')

        word = pp.OneOrMore(pp.Word(pp.alphanums + "'."))
        url = pp.Literal("https://source.unsplash.com/960x640/?")
        u = pp.Literal("(") + url + word + pp.Literal(")")

        def ll(a):
            pass

        datas = []
        urls = []
        idx = 0
        for a, b, c in u.scan_string(s):
            urls.append("".join(a)[1:-1])
            sub = s[idx:b]
            if sub:
                datas.append(sub)
            datas.append("url")
            idx = c
        print(urls)
        print(datas)
