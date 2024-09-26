import logging
from .connection import get_connection, close_connection


def create_user():
    conn = get_connection()
    
    if not conn: return

    cursor = conn.cursor()

    query = """CREATE TABLE IF NOT EXISTS user (
                                id INTEGER PRIMARY KEY,
                                uuid TEXT NOT NULL,
                                username TEXT NOT NULL,
                                device_token TEXT NOT NULL);"""

    cursor.execute(query)
    close_connection(conn)



def create_tables():
    try:
        create_user()
    except Exception as e:
        logging.error("Database tables creation error: ", str(e))

