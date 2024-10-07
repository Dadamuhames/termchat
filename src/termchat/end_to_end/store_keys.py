from termchat.api.chats import send_my_publik_key
from termchat.database.chat_queries import create_chat
from termchat.socket_client import SocketClient
from .generate_keys import generate_keys




def generate_and_store_my_keys_for_chat(chat_id: int):
    privateKey, publicKey = generate_keys()

    create_chat(chat_id, publicKey, privateKey)

    return publicKey, privateKey



async def generate_and_send_my_key(device_token: str, chat_id: int, socket: SocketClient):
    publicKey, privateKey = generate_and_store_my_keys_for_chat(chat_id)

    await send_my_publik_key(device_token, chat_id, publicKey)

    keys = {
        "public_key": publicKey,
        "private_key": privateKey,
    }

    chat_confirm_message = {
        "type": "CONFIRM_CHAT",
        "publicKey": publicKey,
        "chatId": chat_id
    }

    socket.send_message(chat_confirm_message)

    return keys


