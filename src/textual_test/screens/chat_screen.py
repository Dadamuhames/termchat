import threading
from textual.app import ComposeResult, messages
from textual import on
from textual.widgets import Input, Static
from textual.screen import Screen
from datetime import datetime
from textual_test.database.dto import User
from textual_test.database.user_queries import get_user_data
from textual_test.socket_client import SocketClient
from textual_test.widgets.messages import Message, MessageList
from textual.message import Message as TextualMessage


class ChatScreen(Screen):
    username: str
    messages: list[Message]
    socket: SocketClient


    class NewMessage(TextualMessage):
        def __init__(self, data: dict) -> None:
            self.data = data
            super().__init__()

    CSS_PATH = "../tcss/messages.tcss"

    def __init__(self, username: str, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.username = username
        self.messages = list()

        user: User | None = get_user_data()

        assert user != None, "User not found"

        self.socket = SocketClient(user.device_token)
        self.socket.connect()  

    async def new_message_wrap(self, data):
        self.app.call_from_thread(self.new_message, data)
        


    @on(NewMessage)
    async def new_message(self, new_message: NewMessage):
        message_data = new_message.data

        messages_list = self.query_one(MessageList)
    
        message = message_data.get("message", "")
        from_user = message_data.get("from_user_id", "")

        messages_list.messages.append(Message(from_user=str(from_user), message=message, date=datetime.now()))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()



    def on_data_recieved(self, data: dict):
        self.post_message(self.NewMessage(data))


    def compose(self) -> ComposeResult: 
        yield Static(f"Chat: {self.username}", id="chat_label")

        yield MessageList(messages=self.messages)

        yield Input(id="message_input")

        self.run_worker(self.socket.recieve_data(self.on_data_recieved), thread=True)



    @on(Input.Submitted, selector="#message_input")
    async def send_message(self, event: Input.Submitted):
        message: str = event.input.value

        if not len(message): return

        self.socket.send_message({"message": message, "toUserId": 57})

        messages_list = self.query_one(MessageList)

        messages_list.messages.append(Message(message=message, date=datetime.now(), my_message=True))

        await messages_list.recompose()

        messages_list.scroll_end(animate=False)

        self.query_one(Input).clear()

