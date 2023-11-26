import sqlite3


def execute_query(query):
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
