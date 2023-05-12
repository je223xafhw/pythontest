import sqlite3 as sl
import os
from datetime import datetime

con = sl.connect('users.db')


def create():
    with con:
        con.execute("""
            CREATE Table USER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                timestamp INT,
                key TEXT
            );
        """)


def in_db_f(timestamp):
    with con:
        data = con.execute(
            "SELECT * FROM USER WHERE timestamp =" + str(timestamp))
    try:
        id = data.fetchone()[0]
        return id
    except:
        return False


def get_last():
    data = con.execute("SELECT MAX(Id) FROM USER")
    id = data.fetchone()[0]
    return id


def newuser():
    now = datetime.timestamp(datetime.now())
    now = int(now)
    in_db = in_db_f(now)
    if in_db:
        return in_db
    else:
        key = os.urandom(16)
        sql = 'INSERT INTO USER (timestamp, key) values(?, ?)'
        data = [(now, key)]
        with con:
            con.executemany(sql, data)
        return True


def geteverything():
    with con:
        data = con.execute("SELECT * FROM USER")
        for row in data:
            print(row)


try:
    create()
except:
    pass
