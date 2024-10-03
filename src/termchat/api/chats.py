from datetime import datetime
from termchat.database.dto import ChatItem
from termchat.widgets.messages import Message
from .utils import get, post, get_auth_header



async def create_chat(device_token: str, userId: int):
    headers = get_auth_header(device_token)

    data = {"userId": userId}

    return await post("/chats", headers=headers, json=data)


def get_chats(device_token: str) -> list[ChatItem]:
    headers = get_auth_header(device_token)

    chats = get("/chats", headers=headers)

    if not chats: return list()

    chats = [ChatItem(int(chat.get("id", 0)), chat.get("username")) for chat in chats]

    return chats 



def get_chat_inner(device_token: str, chatId: int):
    headers = get_auth_header(device_token)

    return get(f"/chats/{chatId}", headers=headers)

  

def get_chat_messages(device_token: str, chatId: int):
    headers = get_auth_header(device_token)

    messages = get(f"/messages/{chatId}", headers=headers)

    if not messages: return list()


    mapped_messages = list()

    for message in messages.get("messages", list()):
        msg = Message()

        msg.message = message.get("message")

        msg.date = datetime.strptime(message.get("createdAt"), '%Y-%m-%dT%H:%M:%S.%fZ')

        msg.my_message = message.get("myMessage", False)

        mapped_messages.append(msg)

    return mapped_messages

