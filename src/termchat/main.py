from typing import Type
from textual.app import ComposeResult
from textual import on
from textual.driver import Driver
from textual.widgets import Input, Label
import getpass
from termchat.api.chats import get_chats
from termchat.api.users import create_user
from termchat.database.dto import User
from termchat.myapp_base import MyAppBase
from termchat.screens.chats_list_screen import ChatsListScreen
from termchat.database.user_queries import get_user_data, save_user
from termchat.screens.users_screen import UsersScreen
from termchat.socket_client import SocketClient
import uuid
import socket
from textual.types import CSSPathType


class MyApp(MyAppBase):
    device_token: str
    CSS_PATH = "tcss/app.tcss"
    SCREENS = {"users": UsersScreen}
    BINDINGS = [("escape", "go_back", "<-Back"), ("c, ctrl+h", "show_chats", "Chats"), 
                ("u", "push_screen('users')", "Users"), ("q", "custom_quit", "Quit")]


    def __init__(self, driver_class: Type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        self.socket_client = None
        self.chat_list_screen = None
        self.device_token = ""


    def compose(self) -> ComposeResult:
        user: User | None = get_user_data()

        if not user:
            username: str = getpass.getuser()

            label = Label(f"Enter your username (Default: '{username}'):", id="label")

            input = Input(id="username_input")

            yield label
            yield input
        else:
            self.device_token = user.device_token

            self.socket_client = SocketClient(self.device_token)
            self.socket_client.connect()

            self.chat_list_screen = ChatsListScreen(self.device_token, self.socket_client)
            
            self.chat_list_screen.start_worker()  

            self.push_screen(self.chat_list_screen)

            

    async def action_custom_quit(self):
        assert self.socket_client != None

        self.socket_client.close()
        await self.action_quit()


    def action_go_back(self):
        if not isinstance(self.screen, ChatsListScreen):
            self.pop_screen()


    async def action_show_chats(self):
        if not self.socket_client:
            self.socket_client = SocketClient(self.device_token)
            self.socket_client.connect()


        if self.chat_list_screen:
            chats = get_chats(self.device_token)            

            self.chat_list_screen.chats_list = chats

            await self.chat_list_screen.recompose()
            
            self.switch_screen(self.chat_list_screen)

        else:
            self.chat_list_screen = ChatsListScreen(self.device_token, self.socket_client)

            self.chat_list_screen.start_worker()

            self.switch_screen(self.chat_list_screen)



    @on(Input.Submitted, selector="#username_input")
    async def save_username(self, event: Input.Submitted):
        username: str = event.input.value

        if username == "":
            username = getpass.getuser()

        user = User()
        
        user.username = username
        user.device_token = str(uuid.uuid4())

        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)


        user_create_data = {
            "username": username,
            "ip_address": IPAddr,
            "device_token": user.device_token
        }

        user_saved = await create_user(user_create_data)

        if not user_saved or user_saved == None:
            self.notify("Username exists! Pick another one!.... OR GO CRY!", severity="error", timeout=5)
            return

    
        assert user_saved != None, "User is not created"

        user.uuid = user_saved.get("id", 0)

        save_user(user)

     
        self.device_token = user.device_token


        self.socket_client = SocketClient(self.device_token)
        self.socket_client.connect()

        self.chat_list_screen = ChatsListScreen(self.device_token, self.socket_client) 

        self.chat_list_screen.start_worker()

        self.push_screen(self.chat_list_screen)

