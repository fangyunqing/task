# @Time    : 2023/07/06 13:07
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

import copy
import json
import sqlite3

from munch import Munch


def get_record(kind: str, name: str, date: str, params: Munch = None) -> Munch:
    params = params if params else Munch()
    conn = sqlite3.connect(r'record.db')
    conn.row_factory = lambda cur, row: {col[0]: row[idx]
                                         for idx, col in enumerate(cur.description)}
    cursor = conn.cursor()
    try:
        select_sql = ("SELECT kind, name, date, num, memo, params "
                      "FROM record "
                      "WHERE kind=:kind and name=:name and date=:date")
        cursor.execute(select_sql, {
            "kind": kind,
            "name": name,
            "date": date
        })
        select_record = cursor.fetchone()
        if select_record:
            record = Munch(select_record)
            record.memo = Munch(json.loads(record.memo)) if isinstance(record.memo, str) and record.memo else Munch()
            record.params = (Munch(json.loads(record.params))
                             if isinstance(record.params, str) and record.params else params)
            return record
        else:
            record = Munch()
            record.kind = kind
            record.name = name
            record.date = date
            record.num = 0
            record.memo = ""
            record.params = json.dumps(params)
            insert_sql = ("INSERT INTO record(kind, name, date, num, memo, params) "
                          "VALUES(:kind, :name, :date, :num, :memo, :params)")
            cursor.execute(insert_sql, record)
            conn.commit()
            record.params = params
            record.memo = Munch()
            return record
    finally:
        conn.rollback()
        cursor.close()
        conn.close()


def update_record(record: Munch):
    conn = sqlite3.connect(r'record.db')
    cursor = conn.cursor()
    try:
        copy_record = copy.deepcopy(record)
        copy_record.memo = json.dumps(copy_record.memo)
        copy_record.params = json.dumps(copy_record.params)
        update_sql = ("UPDATE record "
                      "SET num=:num, memo=:memo, params=:params "
                      "WHERE kind=:kind and name=:name and date=:date")
        cursor.execute(update_sql, copy_record)
        conn.commit()
    finally:
        conn.rollback()
        cursor.close()
        conn.close()
