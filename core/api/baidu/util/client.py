# @Time    : 2023/06/19 10:03
# @Author  : fyq
# @File    : client.py
# @Software: PyCharm

__author__ = 'fyq'

import random
from dataclasses import dataclass

from core.util.locus import Rectangle, Circle, Point, Shape


@dataclass
class ClientInfo:
    client: Rectangle

    image_verify: Shape

    submit: Shape


_client_info_list = [
    ClientInfo(client=Rectangle(width=1020, height=918, start=Point(0, 0)),
               image_verify=Circle(start=Point(381, 543), radius=25),
               submit=Rectangle(width=326, height=38, start=Point(441, 533))
               ),
    ClientInfo(client=Rectangle(width=1191, height=918, start=Point(0, 0)),
               image_verify=Circle(start=Point(468, 543), radius=25),
               submit=Rectangle(width=326, height=38, start=Point(528, 533))
               ),
    ClientInfo(client=Rectangle(width=876, height=918, start=Point(0, 0)),
               image_verify=Circle(start=Point(305, 543), radius=25),
               submit=Rectangle(width=326, height=38, start=Point(370, 533))
               ),
]


def random_client() -> ClientInfo:
    return random.choice(_client_info_list)
