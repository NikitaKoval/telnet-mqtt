import logging
import socket
from copy import copy
from threading import Thread

from client import ClientFactory


class Server:
    def __init__(self, host, port, client_factory: ClientFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_factory = client_factory
        self._running = False
        self.daemon = True

        self.clients = {}

    def run(self):
        logging.info(f'Server started')
        self._running = True
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

        while self._running:
            conn, addr = self.sock.accept()
            if not conn:
                break
            client = self.client_factory.create_client(conn, addr)
            client.start()
            logging.info(f'Client {addr} connected')
            self.clients[addr] = client

    def stop(self):
        clients = copy(self.clients)
        for addr, client in clients.items():
            client.terminate()
        self._running = False

        self.sock.shutdown(2)
        self.sock.close()
        logging.info(f'Server stopped')