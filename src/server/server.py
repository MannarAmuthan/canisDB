import json
import socket
import sqlite3
import threading
from typing import Dict, Any


class DatabaseServer:
    def __init__(self,
                 host: str = '0.0.0.0',
                 port: int = 5432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = sqlite3.connect('coordinator_init.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Database Server listening on {self.host}:{self.port}")

        while True:
            try:
                print(f"Starting to listen")
                client, address = self.socket.accept()
                print(f"Connection from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.start()
            except Exception as e:
                print(f"Connection error on {e}")

    def handle_client(self, client_socket: socket.socket):
        """Handle individual client connections"""
        while True:
            try:
                # Receive command from client
                data = client_socket.recv(4096).decode()
                if not data:
                    break

                command = json.loads(data)
                response = self.execute_query(command)

                client_socket.send(json.dumps(response).encode())

            except Exception as e:
                print("Error in connecting")
                print(e)
                error_response = {"status": "error", "message": str(e)}
                client_socket.send(json.dumps(error_response).encode())
                break

        client_socket.close()

    def execute_query(self, command: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            try:
                query = command.get("query")
                params = command.get("params", [])

                self.cursor.execute(query, params)

                if query.lower().startswith(("select", "pragma")):
                    results = self.cursor.fetchall()
                    columns = [description[0] for description in self.cursor.description]
                    return {
                        "status": "success",
                        "columns": columns,
                        "rows": results
                    }
                else:
                    self.conn.commit()
                    return {
                        "status": "success",
                        "affected_rows": self.cursor.rowcount
                    }

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
