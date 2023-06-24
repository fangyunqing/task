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
            try:
                await asyncio.sleep(delay)
                print(delay)
                raise ValueError
            except asyncio.CancelledError:
                print("cancel")

        loop = asyncio.get_event_loop()

        task = [
            asyncio.ensure_future(sleep(10)),
            asyncio.ensure_future(sleep(5)),
        ]

        f, p = loop.run_until_complete(asyncio.wait(task, return_when=asyncio.FIRST_EXCEPTION))

        for pp in p:
            pp.cancel()
            loop.run_until_complete(pp)
