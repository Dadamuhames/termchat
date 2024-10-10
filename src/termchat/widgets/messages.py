from datetime import datetime
from rich.console import RenderableType
from textual.app import ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Static


class Message:
    from_user: str | None
    message: str
    date: datetime
    my_message: bool


    def __init__(self, from_user: str | None = None, message: str = "", date: datetime = datetime.now(), my_message: bool = False) -> None:
        self.from_user = from_user
        self.message = message
        self.date = date
        self.my_message = my_message



class MessageBlock(Static):
    message: Message


    def __init__(self,  message: Message, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self.message = message
          

    def render(self) -> RenderResult:
        TEXT = ""

        if self.message.from_user:
            TEXT += f"[b]From:[/b] {self.message.from_user}\n\n"

        TEXT += f"[b]Message:[/b] {self.message.message}\n\n[b]Date:[/b] {self.message.date.strftime('%d/%m/%Y | %H:%M')}"

        return TEXT
    



class MessageList(Widget):
    messages: list[Message]


    def __init__(self, *children: Widget, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False, messages: list[Message] = list()) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.messages = messages


    def compose(self) -> ComposeResult:
        if not self.messages or not len(self.messages):
            yield Static("There is no message yet", id="no_message")
            return

        for message in self.messages:
            if message.my_message:
                yield MessageBlock(message=message, classes="right")
            else:
                yield MessageBlock(message=message)

        self.scroll_end(animate=False)

