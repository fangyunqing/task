# @Time    : 2023/06/06 11:34
# @Author  : fyq
# @File    : test_aio.py
# @Software: PyCharm

__author__ = 'fyq'

import asyncio
import unittest


class TestAio(unittest.TestCase):

    def test_exception(self):
        async def sleep(delay):
            await asyncio.sleep(delay)
            try:
                raise TypeError
            except TypeError:
                if delay == 5:
                    pass
                else:
                    raise TypeError

        def _asyncio_exception_handler(lp, context) -> None:
            pass

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_asyncio_exception_handler)

        task = [
            sleep(10),
            sleep(5),
        ]

        loop.run_until_complete(asyncio.wait(task))
