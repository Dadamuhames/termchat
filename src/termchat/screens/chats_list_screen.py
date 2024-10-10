from textual.app import ComposeResult, on
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static
from textual.worker import Worker

from termchat.api.chats import get_chats
from termchat.database.dto import ChatItem
from termchat.screens.chat_screen import ChatScreen
from termchat.socket_client import SocketClient
from termchat.utils import get_or_generate_chat_keys


class ChatsListScreen(Screen):
    chats_list = reactive(list[ChatItem])
    device_token: str
    socket: SocketClient
    chat_screen: ChatScreen | None
    list_view: ListView | None
    worker: Worker | None

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
        self.list_view = None
        self.worker = None


    
    def compose(self) -> ComposeResult:
        yield Static("Your chats", id="chat_list_label")

        list_items = list()

        for chat in self.chats_list:
            chat_id = f"chat_{chat.id}"
            list_items.append(ListItem(Label(f"@{chat.name}"), id=chat_id))


        self.list_view = ListView(*list_items)

        yield self.list_view
        yield Footer(show_command_palette=False)



    def on_chat_confirmation(self, data: dict):
        if self.chat_screen:
            self.chat_screen.post_message(ChatScreen.ChatComfirmed(data))


    def on_data_recieved(self, data: dict):
        if self.chat_screen:
            self.chat_screen.post_message(ChatScreen.NewMessage(data))

        self.post_message(self.NewMessageInChatList(data)) 


    def start_worker(self):
        self.worker = self.run_worker(self.socket.recieve_data(self.on_data_recieved, self.on_chat_confirmation), thread=True)


    def stop_worker(self):
        if self.worker:
            self.worker.cancel()
            self.worker = None



    @on(ListView.Selected)
    async def chat_selected(self, selected: ListView.Selected):
        chat_id_str = str(selected.item.id)
        chat_id = int(chat_id_str.replace("chat_", ""))

        chat_keys = await get_or_generate_chat_keys(self.device_token, chat_id, self.socket)

        self.chat_screen = ChatScreen(chat_id, self.socket, chat_keys)

        self.app.push_screen(self.chat_screen)



    @on(NewMessageInChatList)
    async def on_new_message(self, message: NewMessageInChatList):
        message_data = message.data

        chats = self.chats_list

        chat_data = message_data.get("chat", {})

        chat_id = int(chat_data.get("id", 0))

        chat = [c for c in chats if c.id == chat_id]

        if len(chat):
            chats.remove(chat[0])

        chats.insert(0, ChatItem(chat_id, chat_data.get("name")))

        self.chats_list = chats

        await self.recompose()

