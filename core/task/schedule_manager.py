# @Time    : 2023/06/01 16:02
# @Author  : fyq
# @File    : schedule_manager.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import Dict, Type, List, Union, Iterable

from munch import Munch

from core.task.abstract_task import ScheduleTask, CombinationTask, schedule_cls_list


class ScheduleManager:

    def __init__(self, opt: Munch):
        self._schedules: Dict[str, List[Type[ScheduleTask]]] = {}
        for schedule_cls in schedule_cls_list:
            self._schedules.setdefault(schedule_cls.login_name, []).append(schedule_cls)
        self._real_task: List[Union[ScheduleTask, CombinationTask]] = []
        self._opt = opt

    def __getitem__(self, item) -> List[Type[ScheduleTask]]:
        return self._schedules.get(item)

    def __iter__(self) -> Iterable[List[Type[ScheduleTask]]]:
        return iter(self._schedules.values())

    @property
    def tasks(self) -> List[Union[ScheduleTask, CombinationTask]]:
        if not self._real_task:
            for k, v in self._schedules.items():
                if len(v) > 1:
                    self._real_task.append(CombinationTask(opt=self._opt,
                                                           login_name=k,
                                                           st_cls_list=v))
                else:
                    self._real_task.append(v[0](self._opt))

        return self._real_task
