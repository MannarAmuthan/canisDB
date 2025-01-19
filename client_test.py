import json
import socket
from typing import Dict, Any


class LocalDatabaseClient:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def execute(self, query: str, params: list = None) -> Dict[str, Any]:
        """Execute a query on the database db_server"""
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


try:
    client = LocalDatabaseClient("127.0.0.1", 5014)

    print(client.execute("""
        CREATE TABLE IF NOT EXISTS central_kv_store (
            key TEXT UNIQUE,
            value TEXT
        )
    """))

    client.close()

except ConnectionRefusedError:
    print("Connection failed - db_server might not be running")
except json.JSONDecodeError:
    print("Received invalid JSON response from db_server")
except Exception as e:
    print(f"Error: {str(e)}")


