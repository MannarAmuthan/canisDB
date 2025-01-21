import json
import socket
from logging import Logger
from typing import Dict, Any

from socket_utils import send_json


class DatabaseClient:
    def __init__(self, logger: Logger):
        self.logger = logger

    def execute(self, host: str, port: int, query: str, params: list = None) -> Dict[str, Any]:
        """Execute a query on the database db_server"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        if params is None:
            params = []

        command = {
            "query": query,
            "params": params
        }

        self.logger.info(f"Started sending command to ({host}: {port})")
        send_json(client_socket, command)
        response = client_socket.recv(4096).decode()
        client_socket.close()
        return json.loads(response)
