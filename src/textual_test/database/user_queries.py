import logging
from .connection import get_connection, close_connection
from .dto import map_to_user, User


def get_user_data() -> User | None:
    conn = get_connection()

    if not conn: return None

    cur = conn.cursor()

    query = f"SELECT id, uuid, username, device_token FROM user"

    res = cur.execute(query)

    row = res.fetchone()

    close_connection(conn)

    return map_to_user(row)


def save_user(user: User):
    conn = get_connection()

    if not conn: return None

    cur = conn.cursor()
    
    user_device_token = user.device_token

    user_data = get_user_data()

    if user_data:
        user_device_token = user_data.device_token 


    query = f"INSERT OR REPLACE INTO user (id, uuid, username, device_token) VALUES (1, ?, ?, ?)"

    #try:
    cur.execute(query, (user.uuid, user.username, user_device_token,))
    close_connection(conn)

