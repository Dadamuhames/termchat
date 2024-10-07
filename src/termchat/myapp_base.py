from textual.app import App
from termchat import socket_client
from termchat.screens.chats_list_screen import ChatsListScreen


class MyAppBase(App):
    socket_client: socket_client.SocketClient | None
    chat_list_screen: ChatsListScreen | None
