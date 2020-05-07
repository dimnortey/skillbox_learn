"""
Серверное приложение для соединений
"""

import asyncio
from asyncio import transports
from typing import Optional


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def check_login(self, login):
        for client in self.server.clients:
            if client.login == login:
                return False
        return True

    def send_history(self):
        for message in self.server.last_messages[-10:]:
            self.transport.write(message.encode())

    def data_received(self, data: bytes):
        decoded = data.decode()

        print(decoded)

        if self.login is None:
            # login:
            if decoded.startswith("login:"):

                login = decoded.replace("login:", "").replace("\r\n", "")
                if self.check_login(login):
                    self.login = login
                    self.transport.write(f"Привет, {self.login}!".encode())
                    self.send_history()
                else:
                    self.transport.write(f"Логин {self.login} занят!".encode())
                    self.server.clients.remove(self)
        else:
            self.send_message(decoded)

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        self.server.last_messages.append(format_string)
        encoded = format_string.encode()
        for client in self.server.clients:
            if client.login != self.login:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено")

    def connection_lost(self, exc: Optional[Exception]):
        print("Соединение разорвано")
        self.server.clients.remove(self)


class Server:
    clients: list
    last_messages: list


    def __init__(self):
        self.clients = []
        self.last_messages = []

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()
        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )
        print("Сервер запущен ...")

        await coroutine.serve_forever()



process = Server()
try:
    asyncio.run(process.start())
except KeybordInterrupt:
    print("Сервер остановлен вручную")
