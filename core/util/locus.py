# @Time    : 2023/06/12 11:41
# @Author  : fyq
# @File    : locus.py
# @Software: PyCharm

__author__ = 'fyq'

import random
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Optional

Point = namedtuple("point", "x,y")


class Shape(metaclass=ABCMeta):

    def __init__(self, start: Point):
        self.start = start

    def __contains__(self, point: Point):
        return self.contains(point)

    @abstractmethod
    def contains(self, point: Point) -> bool:
        pass

    @abstractmethod
    def random(self) -> Point:
        pass

    @abstractmethod
    def random_x(self, y: int) -> Point:
        pass

    @abstractmethod
    def random_y(self, x: int) -> Point:
        pass

    @property
    @abstractmethod
    def center(self) -> Point:
        pass


class Circle(Shape):

    def __init__(self, start: Point, radius: int):
        super().__init__(start)
        self.radius = radius

    def contains(self, point: Point) -> bool:
        distance = (point.x - self.center.x) ** 2 + (point.y - self.center.y) ** 2
        return distance <= self.radius ** 2

    def move(self, distance: Point):
        self.start = Point(self.start.x + distance.x, self.start.y + distance.y)

    def random(self) -> Point:
        range_x = [self.start.x, self.start.x + 2 * self.radius]
        range_y = [self.start.y, self.start.y + 2 * self.radius]
        while True:
            p = Point(random.randint(*range_x), random.randint(*range_y))
            if p in self:
                return p

    def random_x(self, y: int):
        range_x = [self.start.x, self.start.y + 2 * self.radius]
        while True:
            p = Point(random.randint(*range_x), y)
            if p in self:
                return p

    def random_y(self, x: int) -> Point:
        range_y = [self.start.y, self.start.y + 2 * self.radius]
        while True:
            p = Point(x, random.randint(*range_y))
            if p in self:
                return p

    @property
    def center(self) -> Point:
        return Point(self.start.x + self.radius, self.start.y + self.radius)


class Rectangle(Shape):

    def __init__(self, width: int, height: int, start: Point):
        super().__init__(start=start)
        self.width = width
        self.height = height

    def contains(self, point: Point) -> bool:
        return (self.start.x <= point.x <= self.start.x + self.width and
                self.start.y <= point.y <= self.start.y + self.height)

    def random(self) -> Point:
        range_x = [self.start.x, self.start.x + self.width]
        range_y = [self.start.y, self.start.y + self.height]
        return Point(random.randint(*range_x), random.randint(*range_y))

    def random_x(self, y: int) -> Point:
        range_x = [self.start.x, self.start.x + self.width]
        return Point(random.randint(*range_x), y)

    def random_y(self, x: int) -> Point:
        range_y = [self.start.y, self.start.y + self.height]
        return Point(x, random.randint(*range_y))

    @property
    def center(self) -> Point:
        return Point(self.start.x + int(self.width / 2), self.start.y + int(self.height / 2))


@dataclass
class ImitateClientPoints:
    """
    模拟客户点信息
    """
    client: Shape

    points: List[Point] = field(default_factory=lambda: [])


@dataclass
class ImitatePoints:
    """
    模拟点信息
    """
    client: Shape

    component: Shape

    click_point: Optional[Point] = None

    client_points: List[Point] = field(default_factory=lambda: [])

    component_points: List[Point] = field(default_factory=lambda: [])


def imitate_client_locus(client: Shape, point_count: int) -> ImitateClientPoints:
    if point_count < 0:
        point_count = 5
    icp = ImitateClientPoints(client=client)
    for _ in range(0, point_count):
        icp.points.append(client.random())
    return icp


def imitate_locus(client: Shape, component: Shape, move_length: int, client_point_count: int) -> ImitatePoints:
    if client_point_count < 0:
        client_point_count = 5
    # 模拟点
    imitate_points = ImitatePoints(client=client, component=component)

    for _ in range(0, client_point_count):
        imitate_points.client_points.append(client.random())

    # 点击信息
    imitate_points.click_point = component.random()

    if move_length > 0:
        sum_length = 0
        while True:
            random_length = random.randint(-10, 50)
            while random_length + sum_length < 0:
                random_length = random.randint(-10, 50)
            sum_length += random_length
            if sum_length >= move_length:
                break
            imitate_points.component_points.append(Point(x=imitate_points.click_point.x + sum_length,
                                                         y=imitate_points.click_point.y))
    # 最后点信息
    imitate_points.component_points.append(Point(x=imitate_points.click_point.x + move_length,
                                                 y=imitate_points.click_point.y))
    return imitate_points
