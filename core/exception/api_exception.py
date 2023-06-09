# @Time    : 2023/05/31 11:55
# @Author  : fyq
# @File    : api_exception.py
# @Software: PyCharm

__author__ = 'fyq'

from core.exception import TaskException


class ApiException(TaskException):
    pass


class NotFoundApiException(ApiException):
    def __init__(self, api_sign: str):
        super().__init__(f"{api_sign} 404")
