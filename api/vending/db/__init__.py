import sqlite3
from enum import Enum
from typing import Union
from sqlite3 import Error, Connection

DB_NAME = "vending.sql"


class FetchType(Enum):
    ALL = 1
    FIRST = 2
    NONE = 3


def connect() -> Connection:
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Error as e:
        print(e)
        raise e


def execute(
    sql: str, params: dict = {}, fetch: FetchType = FetchType.NONE
) -> Union[list[str], str]:
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = None

        if fetch is FetchType.ALL:
            result = cursor.fetchall()
        elif fetch is FetchType.FIRST:
            result = cursor.fetchone()
        else:
            result = "success"

        conn.commit()
        conn.close()
        return result
    except Error as e:
        print(e)
        raise e


def setup():
    try:
        sqlite3.connect("file:vending.sql?mode=rw", uri=True)
    except sqlite3.OperationalError:
        create_users_table_sql = """CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username CHAR(20) NOT NULL,
            password CHAR(20) NOT NULL,
            deposit INTEGER DEFAULT 0,
            role CHAR(20) NOT NULL
        )"""
        create_products_table_sql = """CREATE TABLE products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_available INTEGER NOT NULL,
            cost INTEGER NOT NULL,
            product_name CHAR(20) NOT NULL,
            seller_id CHAR(20) NOT NULL
        )"""

        try:
            execute(create_users_table_sql)
            execute(create_products_table_sql)
        except Error as e:
            print(e)
            pass
