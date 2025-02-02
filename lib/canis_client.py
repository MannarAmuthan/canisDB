import json
import socket
from typing import Dict, Any


class CanisClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str, port: int):
        self.socket.connect((host, port))

    def execute(self, query: str, params: list[str]):
        command = {
            "query": query,
            "params": params
        }
        self.socket.send(json.dumps(command).encode())
        result = json.loads(self.socket.recv(4096).decode())
        return result

    def close(self):
        """Close the client connection"""
        self.socket.close()
