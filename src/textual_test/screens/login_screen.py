import getpass
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label

class LoginScreen(Screen):
    CSS_PATH = "tcss/app.tcss"

    def compose(self) -> ComposeResult:

        username: str = getpass.getuser()

        label = Label(f"Enter your username (Default: '{username}'):", id="label")

        input = Input(id="username_input")

        yield label
        yield input

