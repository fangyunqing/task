# @Time    : 2023/06/01 16:02
# @Author  : fyq
# @File    : schedule_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Dict, Type, List, Union

from munch import Munch

from core.task.abstract_task import ScheduleTask, CombinationTask


class ScheduleManager:

    def __init__(self, opt: Munch):
        self._schedules: Dict[str, List[Type[ScheduleTask]]] = {}
        self._real_task: List[Union[Type[ScheduleTask], CombinationTask]] = []
        self._opt = opt

    def add_schedule(self,
                     login_name: str,
                     task_type: str,
                     api_types: List[str]):
        def add_schedule_decorator(cls: Type[ScheduleTask]):
            cls.task_type = task_type
            cls.api_types = api_types
            cls.task_name = cls.__name__.replace("Login", "").lower()
            cls.login_name = login_name
            self._schedules.setdefault(cls.login_name, []).append(cls)

        return add_schedule_decorator

    @property
    def tasks(self) -> List[Union[Type[ScheduleTask], CombinationTask]]:
        if not self._real_task:
            for k, v in self._schedules:
                if len(v) > 1:
                    self._real_task.append(CombinationTask(opt=None,
                                                           login_name=k,
                                                           st_cls_list=v))
                else:
                    self._real_task.append(v[0])

        return self._real_task
