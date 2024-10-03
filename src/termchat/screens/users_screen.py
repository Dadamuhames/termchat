import getpass
from textual.app import ComposeResult, on
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Input, Label, ListItem, ListView

from termchat.api.chats import create_chat
from termchat.api.users import get_users, get_users_async
from termchat.database.dto import User, UserListItem
from termchat.database.user_queries import get_user_data
from .chat_screen import ChatScreen



class CustomListItem(ListItem):
    user_id: int
    chat_id: int | None

        
    def __init__(self, *children: Widget, user_id: int, chat_id: int | None = None, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.user_id = user_id
        self.chat_id = chat_id



class UsersScreen(Screen):
    users_list: list[UserListItem]
    device_token: str

    CSS_PATH = "../tcss/list.tcss"

    CSS = """ 
    Screen {
        background: $primary 0%; /* semi-transparent black */
        align: center middle;
        overflow: hidden;
        max-width: 100;
        max-height: 30;
    }


    Input#user_search_input {
        max-width: 70;
        margin-top: 1;
        margin-left: 2;
    }

    
    ListView {
        width: 70;
        height: 30;
        margin: 2 2;
    }


    Static#chat_label {
        border: round white;
        max-width: 70;
        margin-bottom: -1;
        content-align: center middle;
    }


    Static#no_message {
        content-align: center middle;
        max-width: 70;
        height: 25;
    } """

    
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
            self.users_list = get_users(self.device_token, None)

            yield Input(id="user_search_input")

            list_items = list()

            for user_data in self.users_list:
                label = Label(f"@{user_data.name}")
                list_items.append(CustomListItem(label, user_id=user_data.id, chat_id=user_data.chat_id))     

            yield ListView(*list_items)
            yield Footer()
   

    async def change_users_list(self, search: str):
        if len(search) <= 2 and len(search) > 0: return

        users = await get_users_async(self.device_token, search)

        list_view = self.query_one(ListView)
        
        await list_view.clear()

        for user_data in users:
            label = Label(f"@{user_data.name}")
            list_view.append(CustomListItem(label, user_id=user_data.id, chat_id=user_data.chat_id))




    @on(Input.Changed, selector="#user_search_input")
    async def search_users(self, event: Input.Changed):
        search = event.input.value

        self.app.run_worker(self.change_users_list(search), exclusive=True)



    @on(ListView.Selected)
    async def select_user(self, event: ListView.Selected):
        selected = event.item

        if selected.chat_id != None:
            self.app.push_screen(ChatScreen(selected.chat_id, self.app.socket_client))

        else:
            chat_created = await create_chat(self.device_token, selected.user_id)

            self.app.push_screen(ChatScreen(chat_created.get("id"), self.app.socket_client))
            


        print(selected.user_id, selected.chat_id)
