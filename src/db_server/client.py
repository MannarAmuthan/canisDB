import json
import socket
from typing import Dict, Any


class DatabaseClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def execute(self, host: str, port: int, query: str, params: list = None) -> Dict[str, Any]:
        """Execute a query on the database db_server"""
        self.socket.connect((host, port))
        if params is None:
            params = []

        command = {
            "query": query,
            "params": params
        }

        self.socket.send(json.dumps(command).encode())
        response = self.socket.recv(4096).decode()
        self.socket.close()
        return json.loads(response)

    def close(self):
        """Close the client connection"""
        self.socket.close()
