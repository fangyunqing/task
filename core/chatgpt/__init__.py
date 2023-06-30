# @Time    : 2023/06/21 14:33
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

import copy
import json
from json import JSONDecodeError

import aiohttp
import requests
from munch import Munch

import asyncio

_invalid_phrases = ["语言模型",
                    "抱歉",
                    "版权",
                    "未经授权",
                    "AI",
                    "具体的答案",
                    "尽力回答",
                    "更多的信息和图片",
                    "提供解答",
                    "提供的信息有限",
                    "提供帮助"]


async def invoke_3d5_turbo(question: str) -> Munch:
    url = ("https://api-gpt-api.douzhuli.shop/chatgpt/create?"
           "securityKey=QQzImz0a1ImzOBapVquS3Pt1BQ9dxMrN0TPwXNmMSnOP8Gm3ozzwrMy1iySm&"
           "_token_=720a95f77ab3545a2d8cb00bc07f45cc3ed05a010d18071e9f987b7e990c386a")

    # 发送数据
    send_data = {
        "messageType": "chat",  # 固定值
        "modelVersion": 'gpt-3.5-turbo',  # gpt-3.5-turbo | gpt-4
        "askMode": "qa",  # qa | chat (qa: 一问一答， chat: 对话模式，消耗 token 比较快)
        "query": {
            "websiteUserId": "10",  # string, 你网站用户的id，供 GPT 记忆，选填
            "settingInfo": {
                "temperature": 0.2,  # float32
                "presencePenalty": 0.2,  # float32
            }
        },
        "messages": [
            {
                "role": "user",
                "content": question
            },
        ],
    }
    # 发送post请求 , 一般来说，GPT 3.5 在 120秒之内差不多
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=send_data) as response:
                text = await response.read()
                if text:
                    try:
                        m = Munch(json.loads(text))
                        if m.success:
                            data: str = copy.copy(m.data)
                            if not any([ip in data for ip in _invalid_phrases]):
                                return Munch({
                                    "a": data,
                                    "sa": m.data
                                })
                    except JSONDecodeError:
                        pass
    except asyncio.exceptions.TimeoutError:
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()


    async def invoke():
        data = await invoke_3d5_turbo("你好")
        print(data)


    loop.run_until_complete(asyncio.wait([asyncio.ensure_future(invoke())]))
