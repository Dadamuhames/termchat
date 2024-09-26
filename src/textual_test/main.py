import asyncio
import threading
from typing import Type
from textual.app import App, ComposeResult
from textual import on
from textual.driver import Driver
from textual.widgets import Input, Label
import getpass
from textual_test.api.users import create_user
from textual_test.database.dto import User
from textual_test.screens.chat_screen import ChatScreen
from textual_test.database.user_queries import get_user_data, save_user
from textual_test.screens.login_screen import LoginScreen
from textual_test.socket_client import SocketClient
import uuid
import socket


class MyApp(App):
    socket: SocketClient
    CSS_PATH = "tcss/app.tcss"


    def __init__(self, driver_class: Type[Driver] | None = None, css_path = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)



    def compose(self) -> ComposeResult:
        user: User | None = get_user_data()

        if not user:
            yield LoginScreen()

        else:
            chat_screen = ChatScreen(user.username)

            self.push_screen(chat_screen)


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
    
        assert user_saved != None, "User is not created"

        user.uuid = user_saved.get("id", "")

        save_user(user)

        chat_screen = ChatScreen(username)

        self.push_screen(chat_screen)

