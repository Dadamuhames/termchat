from collections.abc import Callable
import socket
import json


HOST = "127.0.0.1"
PORT = 7070


class SocketClient:
    _connection: socket.socket
    device_token: str
    connected: bool

    def __init__(self, device_token: str) -> None:
        self.device_token = device_token
        self.connected = False


    def on_message(self, data):
        message = json.loads(str(data.decode()))
        
        print("New message:")
        print(message)


    async def recieve_data(self, handler: Callable):
        while True:
            data = self._connection.recv(2048)

            if data != None and data.decode() != "":
                handler(json.loads(data.decode()))



    def connect(self):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        self._connection.connect((HOST, PORT))

        self.connected = True

        message = {
            "deviceToken": self.device_token,
            "type": "AUTH"
        }

        self._connection.sendall(bytes(json.dumps(message), encoding='utf-8'))



    def close(self):
        self.connected = False
        self._connection.close()


    def send_message(self, message: dict):
        message["deviceToken"] = self.device_token

        message_in_bytes = bytes(json.dumps(message), encoding="utf-8")

        self._connection.send(message_in_bytes)

