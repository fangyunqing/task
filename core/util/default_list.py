# @Time    : 2023/03/25 8:40
# @Author  : fyq
# @File    : default_list.py
# @Software: PyCharm

__author__ = 'fyq'

from operator import __getitem__
from typing import overload, List


class DefaultList(list):
    """
        默认list
        当访问超出索引值的时候返回0 而不会抛出IndexError
    """

    @overload
    def __getitem__(self, i: int) -> __getitem__: ...

    @overload
    def __getitem__(self, s: slice) -> List[__getitem__]: ...

    def __getitem__(self, i: int) -> __getitem__:
        try:
            return super().__getitem__(i)
        except IndexError:
            return 0


if __name__ == "__main__":
    d = DefaultList()
    d.append(3)
    print(d[4])
