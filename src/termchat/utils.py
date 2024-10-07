from termchat.database.chat_queries import get_chat_keys
from termchat.end_to_end.store_keys import generate_and_send_my_key
from termchat.socket_client import SocketClient


async def get_or_generate_chat_keys(device_token: str, chat_id: int, socket: SocketClient):
    chat_keys = get_chat_keys(chat_id)

    return await generate_chat_keys_if_not_exists(chat_keys, device_token, chat_id, socket)



async def generate_chat_keys_if_not_exists(chat_keys: dict | None, device_token: str, chat_id: int, socket: SocketClient):
    # check private/publick key existance othervice create
    if not chat_keys:
        chat_keys = await generate_and_send_my_key(device_token, chat_id, socket)

    return chat_keys

