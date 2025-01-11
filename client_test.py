import json
import socket
from typing import Dict, Any


class DatabaseClient:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def execute(self, query: str, params: list = None) -> Dict[str, Any]:
        """Execute a query on the database server"""
        if params is None:
            params = []

        command = {
            "query": query,
            "params": params
        }

        self.socket.send(json.dumps(command).encode())
        response = self.socket.recv(4096).decode()
        return json.loads(response)

    def close(self):
        """Close the client connection"""
        self.socket.close()


client = DatabaseClient("localhost",5001)


print(client.execute("""
    CREATE TABLE IF NOT EXISTS central_kv_store (
        key TEXT UNIQUE,
        value TEXT
    )
"""))

client.close()