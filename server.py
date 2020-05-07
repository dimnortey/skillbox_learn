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

    def data_received(self, data: bytes):
        decoded = data.decode()

        print(decoded)

        if self.login is None:
            # login:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                self.transport.write(
                    f"Привет, {self.login}!".encode()
                )
        else:
            self.send_message(decoded)
            self.transport.write(decoded)

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()
        for login, client in self.server.clients.items():
            if login != self.login:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.update({self.login: self})
        print("Соединение установлено")

    def connection_lost(self, exc: Optional[Exception]):
        print("Соединение установлено")
        self.server.clients.pop(self.login)


class Server:
    clients: dist

    def __init__(self):
        self.clients = {}

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
