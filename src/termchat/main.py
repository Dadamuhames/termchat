from textual.app import App, ComposeResult
from textual import on
from textual.binding import Binding
from textual.widgets import Input, Label
import getpass
from termchat.api.users import create_user
from termchat.database.dto import User
from termchat.screens.chats_list_screen import ChatsListScreen
from termchat.database.user_queries import get_user_data, save_user
from termchat.screens.users_screen import UsersScreen
from termchat.socket_client import SocketClient
import uuid
import socket


class MyApp(App):
    socket_client: SocketClient
    device_token: str
    CSS_PATH = "tcss/app.tcss"
    SCREENS = {"users": UsersScreen}
    BINDINGS = [Binding("escape", "go_back", "<-Back"), ("c, ctrl+h", "show_chats", "Chats"), ("u", "push_screen('users')", "Users"), ("q", "custom_quit", "Quit")]

    def compose(self) -> ComposeResult:
        user: User | None = get_user_data()

        if not user:
            username: str = getpass.getuser()

            label = Label(f"Enter your username (Default: '{username}'):", id="label")

            input = Input(id="username_input")

            yield label
            yield input
        else:
            self.socket_client = SocketClient(user.device_token)
            self.socket_client.connect()
            self.device_token = user.device_token
            chats_list_screen = ChatsListScreen(user.device_token, self.socket_client)

            self.push_screen(chats_list_screen)
    


    async def action_custom_quit(self):
        self.socket_client.close()
        await self.action_quit()


    def action_go_back(self):
        if not isinstance(self.screen, ChatsListScreen):
            self.pop_screen()


    def action_show_chats(self):
        if not self.socket_client:
            self.socket_client = SocketClient(self.device_token)
            self.socket_client.connect()


        chats_list_screen = ChatsListScreen(self.device_token, self.socket_client)

        self.push_screen(chats_list_screen)



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

        self.socket_client = SocketClient(user.device_token)
        self.socket_client.connect()
        chats_list_screen = ChatsListScreen(user.device_token, self.socket_client)

        self.device_token = user.device_token

        self.push_screen(chats_list_screen)

