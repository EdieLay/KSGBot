import sqlite3
from threading import Lock

lock = Lock()


def execute_query(query):
    with lock:
        print(query)
        con = sqlite3.connect('chats.db')
        cur = con.cursor()
        con.execute('PRAGMA foreign_keys = ON')
        cur.execute(query)
        con.commit()
        rows = cur.fetchall()
        print(rows)
        cur.close()
        con.close()
        return rows
