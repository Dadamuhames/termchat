from textual.app import ComposeResult
from textual import on
from textual.widgets import Input, Static
from textual.screen import Screen
from datetime import datetime
from termchat.api.chats import get_chat_inner, get_chat_messages
from termchat.database.dto import User
from termchat.database.user_queries import get_user_data
from termchat.end_to_end.decrypt import decrypt_message
from termchat.end_to_end.generate_keys import encrypt_message_for_sending
from termchat.socket_client import SocketClient
from termchat.utils import generate_chat_keys_if_not_exists
from termchat.widgets.messages import Message, MessageList
from textual.message import Message as TextualMessage


class ChatScreen(Screen):
    chat_id: int
    chat_data: dict
    messages: list[Message]
    socket: SocketClient
    listening: bool
    user: User
    keys: dict
 

    class NewMessage(TextualMessage):
        def __init__(self, data: dict) -> None:
            super().__init__()
            self.data = data


    class ChatComfirmed(TextualMessage):
        def __init__(self, data: dict) -> None:
            super().__init__()
            self.data = data
    

    CSS_PATH = "../tcss/messages.tcss"


    def __init__(self, chat_id: int, socket: SocketClient, keys: dict, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.chat_id = chat_id
        self.socket = socket
        self.listening = False
        self.keys = keys

        user: User | None = get_user_data()

        assert user != None, "User not found"

        self.user = user
       
        self.chat_data = get_chat_inner(user.device_token, self.chat_id)
        self.messages = get_chat_messages(user.device_token, self.chat_id)

        assert self.chat_data != None, "Chat should not be null"



    def compose(self) -> ComposeResult: 
        yield Static(f"Chat: {self.chat_data.get('companionName')}", id="chat_label")

        yield MessageList(messages=self.messages)

        yield Input(id="message_input")


    @on(ChatComfirmed)
    async def chat_comfirmed(self, message: ChatComfirmed):
        data = message.data

        self.chat_data["publicKey"] = data.get("publicKey", "")

        self.notify("Companion comfirmed your chat!", severity="information", timeout=5)


    @on(NewMessage)
    async def new_message(self, new_message: NewMessage):
        message_data = new_message.data

        messages_list = self.query_one(MessageList)
    
        message = message_data.get("message", "")


        chat_keys = self.keys

        if not chat_keys:
            self.notify("Chat is not available! You lost it! Go cry!", severity="error", timeout=10)
            return

        message_decr = decrypt_message(message, chat_keys.get("private_key", ""))

        messages_list.messages.append(Message(message=message_decr, date=datetime.now()))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()


    @on(Input.Submitted, selector="#message_input")
    async def send_message(self, event: Input.Submitted):
        message: str = event.input.value.strip()

        if not len(message): return

        # check private/publick key existance othervice create
        chat_keys = await generate_chat_keys_if_not_exists(self.keys, self.user.device_token, self.chat_id, self.socket)

        my_public_key = chat_keys.get("public_key", "")
        companion_public_key = self.chat_data.get("publicKey")

        if not companion_public_key:
            self.notify("Your companion has not comfirmed chat yet!", severity="warning")
            return


        # encrpy message for both users and pack it in json object
        encrypted_message = encrypt_message_for_sending(message, 
                                                        my_public_key, 
                                                        companion_public_key, 
                                                        self.user.uuid, 
                                                        self.chat_data.get("companionId", 0))


        self.socket.send_chat_message({"message": encrypted_message, "chatId": self.chat_id})

        messages_list = self.query_one(MessageList)

        messages_list.messages.append(Message(message=message, date=datetime.now(), my_message=True))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()

