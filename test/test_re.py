# @Time    : 2023/06/24 15:13
# @Author  : fyq
# @File    : test_re.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
import pyparsing as pp


class TestRe(unittest.TestCase):

    def test_one(self):
        s = ('白俄罗斯族是中国的一个少数民族，主要分布在新疆维吾尔自治区伊犁哈萨克自治州、塔城地区和阿勒泰地区。根据2010年的人口普查数据，白俄罗斯族人口为1,387人。'
             '民族英雄方面，白俄罗斯族有一位著名的民族英雄——阿列克谢·米哈伊洛维奇·斯特罗加诺夫（Алексей Михайлович Строганов），他是苏联红军的一名狙击手，曾在二战期间击毙了德国军队中的多名高级军官'
             '生活习俗方面，白俄罗斯族有着独特的传统文化和风俗习惯。以下是一些具体的介绍和案例：'
             '1.服饰：白俄罗斯族的传统服饰以白色为主色调，女性的头上戴着花环或者用丝巾包裹头发，男性则戴着黑色的帽子。以下是一张白俄罗斯族女性穿着传统服饰的图片：'
             '![白俄罗斯族女性穿着传统服饰](https://source.unsplash.com/960×640/?belarusian%20traditional%20clothing)'
             '2.音乐舞蹈：白俄罗斯族有着丰富多彩的音乐和舞蹈文化，其中最著名的是白俄罗斯民间舞蹈。以下是一张白俄罗斯族人在跳舞的图片：'
             '![白俄罗斯族人跳舞](https://source.unsplash.com/960×640/?belarusian%20dance)'
             '3.美食：白俄罗斯族的传统美食以土豆、面包和肉类为主要食材，其中最著名的是白俄罗斯的黑面包。以下是一张白俄罗斯黑面包的图片：'
             '![白俄罗斯黑面包](https://source.unsplash.com/960×640/?belarusian%20black%20bread)'
             '4.节日：白俄罗斯族的传统节日有很多，其中最重要的是复活节和圣诞节。在复活节期间，白俄罗斯族人会在家里准备复活节蛋和复活节面包，同时还会举行各种庆祝活动。以下是一张白俄罗斯复活节蛋的图片：'
             '![白俄罗斯复活节蛋](https://source.unsplash.com/960×640/?belarusian%20easter%20egg)'
             '以上是关于白俄罗斯族的一些资料和习俗介绍，希望对您有所帮助')

        word = pp.OneOrMore(pp.Word(pp.pyparsing_unicode.alphanums + "'.,+-*!#$&%20"))
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
