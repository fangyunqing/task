# @Time    : 2023/07/27 10:45
# @Author  : fyq
# @File    : __init__.py.py
# @Software: PyCharm

__author__ = 'fyq'

import sqlite3
from typing import List


def insert(package_id: int, q_list: List, status=0):
    conn = sqlite3.connect(r'record.db')
    cursor = conn.cursor()
    try:
        q_list = [
            {
                "title": q[0],
                "qid": q[1],
                "id": package_id,
                "status": status
            }
            for q in q_list]
        insert_sql = ("INSERT INTO treasure(title, qid, id, status) "
                      "VALUES(:title, :qid, :id, :status)")
        cursor.executemany(insert_sql, q_list)
        conn.commit()
    finally:
        conn.rollback()
        cursor.close()
        conn.close()


def exist(package_id: int, title: str, qid: str):
    conn = sqlite3.connect(r'record.db')
    cursor = conn.cursor()
    try:
        d = {
            "title": title,
            "qid": qid,
            "id": package_id,
        }
        select_sql = ("SELECT 1 "
                      "FROM treasure "
                      "WHERE id=:id and (title=:title or qid=:qid)")
        cursor.execute(select_sql, d)
        res = cursor.fetchone()
        return res is not None
    finally:
        cursor.close()
        conn.close()

