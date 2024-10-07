from collections.abc import Callable
import socket
import json
import select

HOST = "127.0.0.1"
PORT = 7070


class SocketClient:
    _connection: socket.socket
    device_token: str
    connected: bool

    def __init__(self, device_token: str) -> None:
        self.device_token = device_token
        self.connected = False


    async def recieve_data(self, message_handler: Callable, chat_confirm_handler: Callable):
        while True:
            read_sockets, _, _ = select.select([self._connection], [], [], 100)

            for sock in read_sockets:
                data = self.recv_all(sock)

                if data == None or data == "": continue

                data_as_json = json.loads(data)

                data_type = data_as_json.get("type")

                if data_type == "MESSAGE":
                    message_handler(data_as_json)

                elif data_type == "CONFIRM_CHAT":
                    chat_confirm_handler(data_as_json)



    def recv_all(self, sock: socket.socket):
        result = ""

        while not self.is_json(result):
            data = sock.recv(256)

            if data != None and data.decode() != "":
                result += data.decode()

        return result

        


    def is_json(self, json_str):
        try:
            json.loads(json_str)
        except ValueError:
            return False

        return True


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

        self._connection.sendall(message_in_bytes)

