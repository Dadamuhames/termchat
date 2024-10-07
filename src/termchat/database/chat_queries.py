import logging
from .connection import get_connection, close_connection


def get_chat_keys(chat_id: int):
    conn = get_connection()

    if not conn: return None

    cur = conn.cursor()

    query = f"SELECT public_key, private_key FROM chat WHERE chat_id = ?"

    res = cur.execute(query, (chat_id,))

    row = res.fetchone()

    close_connection(conn)

    if not row: return None

    keys = {
        "public_key": row[0],
        "private_key": row[1],
    }

    return keys


def create_chat(chat_id: int, public_key: str, private_key: str):
    conn = get_connection()

    if not conn: return

    cur = conn.cursor()
    
    chat = get_chat_keys(chat_id)

    if chat != None: return

    query = f"INSERT OR REPLACE INTO chat (chat_id, public_key, private_key) VALUES (?, ?, ?)"

    try:
        cur.execute(query, (chat_id, public_key, private_key,))
    except Exception as e: 
        logging.error(f"Chat creation error: {str(e)}")

    close_connection(conn)

