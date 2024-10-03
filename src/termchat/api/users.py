from termchat.database.dto import UserListItem
from .utils import get_auth_header, post, get



async def create_user(data: dict) -> dict | None:
    return await post("/users", data)


def get_users(device_token: str, search: str | None) -> list[UserListItem]:
    headers = get_auth_header(device_token)

    response_data = get("/users", params={"search": search}, headers=headers)

    users: list[UserListItem] = list()

    for data in response_data.get("result", list()):
        user = UserListItem(data.get("id"), data.get("username"), data.get("chat_id", None))
        users.append(user)

    return users


async def get_users_async(device_token: str, search: str | None):
    return get_users(device_token, search)
