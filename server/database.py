import sqlite3
from commons.config import database

def initialize_sqlite():
    con = sqlite3.connect(database)
    print("Database opened successfully")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(80) UNIQUE NOT NULL, password VARCHAR(80), meta VARCHAR(300));"
    )
    con.commit()
    con.close()


def add_default_user():
    con = None
    try:
        with sqlite3.connect(database) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT into User (username, password, meta) values (?,?,?);",
                ("admin", "admin", ""),
            )
            con.commit()
    except:
        con.rollback()
    finally:
        con.close()

