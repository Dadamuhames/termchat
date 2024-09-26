import logging
import sqlite3


def get_connection() -> sqlite3.Connection | None:
    connection = None

    try:
        connection = sqlite3.connect("termchat.db")
    except Exception as e:
        logging.error("Database creation error: ", str(e))

    return connection


def close_connection(conn: sqlite3.Connection):
    conn.commit()
    conn.cursor().close()
    conn.close()

