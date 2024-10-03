from textual.app import ComposeResult
from textual import on
from textual.widgets import Input, Static
from textual.screen import Screen
from datetime import datetime
from termchat.api.chats import get_chat_inner, get_chat_messages
from termchat.database.dto import User
from termchat.database.user_queries import get_user_data
from termchat.socket_client import SocketClient
from termchat.widgets.messages import Message, MessageList
from textual.message import Message as TextualMessage


class ChatScreen(Screen):
    chat_id: int
    chat_data: dict
    messages: list[Message]
    socket: SocketClient
    listening: bool
 

    class NewMessage(TextualMessage):
        def __init__(self, data: dict) -> None:
            self.data = data
            super().__init__()

    CSS_PATH = "../tcss/messages.tcss"


    def __init__(self, chat_id: int, socket: SocketClient, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.chat_id = chat_id
        self.socket = socket
        self.listening = False

        user: User | None = get_user_data()

        assert user != None, "User not found"
       
        self.chat_data = get_chat_inner(user.device_token, self.chat_id)
        self.messages = get_chat_messages(user.device_token, self.chat_id)

        assert self.chat_data != None, "Chat should not be null"


    @on(NewMessage)
    async def new_message(self, new_message: NewMessage):
        message_data = new_message.data

        messages_list = self.query_one(MessageList)
    
        message = message_data.get("message", "")

        messages_list.messages.append(Message(message=message, date=datetime.now()))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()


    def compose(self) -> ComposeResult: 
        yield Static(f"Chat: {self.chat_data.get('id')}", id="chat_label")

        yield MessageList(messages=self.messages)

        yield Input(id="message_input")



    @on(Input.Submitted, selector="#message_input")
    async def send_message(self, event: Input.Submitted):
        message: str = event.input.value

        if not len(message): return

        self.socket.send_message({"message": message, "chatId": self.chat_data.get("id")})

        messages_list = self.query_one(MessageList)

        messages_list.messages.append(Message(message=message, date=datetime.now(), my_message=True))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()

