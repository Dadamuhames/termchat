from textual.app import ComposeResult, on
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static

from termchat.api.chats import get_chats
from termchat.database.dto import ChatItem
from termchat.screens.chat_screen import ChatScreen
from termchat.socket_client import SocketClient


class ChatsListScreen(Screen):
    chats_list: list[ChatItem]
    device_token: str
    socket: SocketClient
    chat_screen: ChatScreen | None

    CSS_PATH = "../tcss/list.tcss"
    
    class NewMessageInChatList(Message):
        def __init__(self, data: dict) -> None:
            self.data = data
            super().__init__()


    def __init__(self, device_token: str, socket: SocketClient, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.device_token = device_token
        self.chats_list = get_chats(device_token)
        self.chat_screen = None
        self.socket = socket



    def on_data_recieved(self, data: dict):
        if self.chat_screen:
            self.chat_screen.post_message(ChatScreen.NewMessage(data))

        self.app.post_message(self.NewMessageInChatList(data)) 



    def compose(self) -> ComposeResult:
        yield Static("Your chats", id="chat_list_label")

        list_items = list()

        for chat in self.chats_list:
            chat_id = f"chat_{chat.id}"
            list_items.append(ListItem(Label(f"@{chat.name}"), id=chat_id))


        yield ListView(*list_items)
        yield Footer(show_command_palette=False)


        self.run_worker(self.socket.recieve_data(self.on_data_recieved), thread=True)



    @on(ListView.Selected)
    def chat_selected(self, selected: ListView.Selected):
        chat_id_str = str(selected.item.id)
        chat_id = int(chat_id_str.replace("chat_", ""))


        self.chat_screen = ChatScreen(chat_id, self.socket)

        self.app.push_screen(self.chat_screen)



    @on(NewMessageInChatList)
    async def on_new_message(self, message: NewMessageInChatList):
        message_data = message.data

        chat_data = message_data.get("chat", {})

        chat_id = int(chat_data.get("id", 0))

        chatItem = self.query_one(f"#chat_{chat_id}")

        chatItem.remove()


        chat_id_as_int = int(str(chat_id).replace("chat_", ""))

        self.chats_list.insert(0, ChatItem(chat_id_as_int, chat_data.get("name")))


        chat = [i for i in range(len(self.chats_list)) if self.chats_list[i].id == chat_id]

        if len(chat):
            del self.chats_list[chat[0]]


        await self.recompose()

