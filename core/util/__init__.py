# @Time    : 2023/05/30 16:13
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import List, Dict, Union


def to_list(value: Union[List[str], Dict[str, str], str],
            add_symbol: bool = False,
            remove_key: bool = False) -> List[str]:
    assert value is not None
    if isinstance(value, str):
        assert len(value) > 0
        return [value]
    elif isinstance(value, List):
        return value
    elif isinstance(value, Dict):
        if remove_key:
            return list(value.values())
        else:
            if add_symbol:
                return [f"{k}：【{value}】" for k, v in value.items()]
            else:
                return [f"{k}：{value}" for k, v in value.items()]
    else:
        raise Exception("不支持的类型")


