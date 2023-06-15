# @Time    : 2023/06/12 11:41
# @Author  : fyq
# @File    : locus.py
# @Software: PyCharm

__author__ = 'fyq'

from collections import namedtuple
from dataclasses import dataclass, field
from typing import Tuple, List, Optional
import random

Point = namedtuple("point", "x,y")

_info_list = [
    {
        "clientHeight": 918,
        "clientWidth": 970,
        "left": 357,
        "top": 540
    },
    {
        "clientHeight": 918,
        "clientWidth": 1023,
        "left": 385,
        "top": 540
    },
    {
        "clientHeight": 918,
        "clientWidth": 1195,
        "left": 470,
        "top": 540
    },
]


class Circle:

    def __init__(self, start: Point, radius: int):
        self.start = start
        self.radius = radius
        self.center = Point(start.x + radius, start.y + radius)

    def __contains__(self, point: Point):
        distance = (point.x - self.center.x) ** 2 + (point.y - self.center.y) ** 2
        return distance <= self.radius ** 2

    def move(self, distance: Point):
        self.center = Point(self.center.x + distance.x, self.center.y + distance.y)
        self.start = Point(self.start.x + distance.x, self.start.y + distance.y)

    def random(self) -> Point:
        range_x = [self.start.x, self.start.x + 2 * self.radius]
        range_y = [self.start.y, self.start.y + 2 * self.radius]
        while True:
            p = Point(random.randint(*range_x), random.randint(*range_y))
            if p in self:
                return p

    def random_x(self, fixed: int):
        range_x = [self.start[0], self.start[0] + 2 * self.radius]
        while True:
            p = Point(random.randint(*range_x), fixed)
            if p in self:
                return p


@dataclass
class ImitatePoints:
    """
    模拟点信息
    """
    client_height: int

    client_width: int

    click_point: Optional[Point] = None

    error_points: List[Point] = field(default_factory=lambda: [])

    right_points: List[Point] = field(default_factory=lambda: [])


def imitate_locus(side: int, length: int, angel_length: int, errors: int = 10) -> ImitatePoints:
    """
    模拟轨迹
    :param side: 半径
    :param length: 长度
    :param angel_length: 角度
    :param errors: 错误点个数
    :return:
    """
    if errors < 0:
        errors = 5
    # 随机选择信息
    info = random.choice(_info_list)
    # 模拟点
    imitate_points = ImitatePoints(client_width=info["clientWidth"],
                                   client_height=info["clientHeight"])

    for _ in range(0, errors):
        x = random.randint(0, imitate_points.client_width)
        y = random.randint(0, imitate_points.client_height)
        imitate_points.error_points.append(Point(x, y))

    # 圆按钮
    circle = Circle(Point(info["left"], info["top"]), side)
    # 点击信息
    imitate_points.click_point = circle.random()
    # 模拟滑块信息
    sum_length = 0
    while True:
        random_length = random.randint(-10, 50)
        while random_length + sum_length < 0:
            random_length = random.randint(-10, 50)
        sum_length += random_length
        if sum_length >= angel_length:
            break
        imitate_points.right_points.append(Point(x=imitate_points.click_point.x + sum_length,
                                                 y=imitate_points.click_point.y))
    # 最后点信息
    imitate_points.right_points.append(Point(x=imitate_points.click_point.x + angel_length,
                                             y=imitate_points.click_point.y))
    return imitate_points


if __name__ == "__main__":
    print(imitate_locus(25, 212, 90))
