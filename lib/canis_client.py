import json
import socket
from typing import Dict, Any


class CanisClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str, port: int):
        try:
            self.socket.connect((host, port))
        except Exception as exception:
            print("Could not connect to canis db servers")
            raise exception

    def execute(self, query: str, params = None):
        if params is None:
            params = []
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
