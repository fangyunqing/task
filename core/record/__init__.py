# @Time    : 2023/07/06 13:07
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

import sqlite3

from munch import Munch


def get_record(record: Munch) -> Munch:
    conn = sqlite3.connect(r'record.db')
    conn.row_factory = lambda cur, row: {col[0]: row[idx]
                                         for idx, col in enumerate(cur.description)}
    cursor = conn.cursor()
    try:
        select_sql = "SELECT kind, name, date, num FROM record WHERE kind=:kind and name=:name and date=:date"
        cursor.execute(select_sql, record)
        select_record = cursor.fetchone()
        if select_record:
            return Munch(select_record)
        else:
            record.num = 0
            insert_sql = "INSERT INTO record(kind, name, date, num) VALUES(:kind, :name, :date, :num)"
            cursor.execute(insert_sql, record)
            conn.commit()
            return record
    finally:
        conn.rollback()
        cursor.close()
        conn.close()


def update_record(record: Munch):
    conn = sqlite3.connect(r'record.db')
    cursor = conn.cursor()
    try:
        update_sql = "UPDATE record SET num=:num WHERE kind=:kind and name=:name and date=:date"
        cursor.execute(update_sql, record)
        conn.commit()
    finally:
        conn.rollback()
        cursor.close()
        conn.close()
