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



def create_chat():
    conn = get_connection()

    if not conn: return

    cursor = conn.cursor()

    query = """CREATE TABLE IF NOT EXISTS chat (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER NOT NULL UNIQUE,
                    public_key TEXT NOT NULL,
                    private_key TEXT NOT NULL);"""


    cursor.execute(query)
    close_connection(conn)



def create_tables():
    try:
        create_user()
        create_chat()
    except Exception as e:
        logging.error("Database tables creation error: ", str(e))

