from sqlite3 import Row


class User:
    id: int
    uuid: str
    username_changed: bool
    username: str
    device_token: str


def map_to_user(row: Row):
    if not row: return None

    user = User()

    user.id = row[0]
    user.uuid = row[1]
    user.username = row[2]
    user.device_token = row[3]

    return user

