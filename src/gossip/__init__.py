import json
import socket
import threading
from logging import Logger


class GossipService:
    def __init__(self,
                 host,
                 port: int,
                 logger: Logger):
        self.host = host
        self.port = port
        self.logger = logger

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.logger.info(f"Internal Listener listening on {self.host}:{self.port}")

        while True:
            try:
                self.logger.info(f"Starting to listen")
                client, address = self.socket.accept()
                self.logger.info(f"Connection from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.start()
            except Exception as e:
                self.logger.info(f"Connection error on {e}")

    def handle_client(self, client_socket: socket.socket):
        """Handle individual client connections"""
        while True:
            try:
                data = client_socket.recv(4096).decode()
                if not data:
                    break

                request = json.loads(data)

                if request['code'] == 'health':
                    client_socket.send(json.dumps({
                        'response': 'success'
                    }).encode())

                client_socket.send(json.dumps({'response': 'code not found'}).encode())

            except Exception as e:
                self.logger.error("Error in connecting")
                self.logger.error(e)
                error_response = {"status": "error", "message": str(e)}
                client_socket.send(json.dumps(error_response).encode())
                break

        client_socket.close()
