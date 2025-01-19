import json
import socket
import sqlite3
import threading
from logging import Logger
from typing import Dict, Any

from context import Context
from db_logger import QueryLoggerFactory, WALLoggerFactory
from db_server.client import DatabaseClient
from sql.classifier import is_write_operation


class DatabaseServer:
    def __init__(self,
                 host,
                 port: int,
                 logger: Logger,
                 is_replication_server: bool,
                 database_client: DatabaseClient):
        self.host = host
        self.port = port
        self.logger: Logger = logger
        self.is_replication_server = is_replication_server
        self.database_client = database_client

        self.transaction_logger = QueryLoggerFactory.get_logger()
        self.wal_logger = WALLoggerFactory.get_logger()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn = sqlite3.connect(f'{Context.get_folder()}/database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def start(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.logger.info(f"Database Server listening on {self.host}:{self.port}")

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
                # Receive command from client
                data = client_socket.recv(4096).decode()
                if not data:
                    break

                command = json.loads(data)
                self.transaction_logger.info(msg=command)

                if is_write_operation(command['query']):
                    self.logger.info("Logging into WAL")
                    self.wal_logger.info(msg=command)
                    if not self.is_replication_server:
                        self.replicate(command)

                response = self.execute_query(command)

                client_socket.send(json.dumps(response).encode())

            except Exception as e:
                self.logger.error("Error in connecting")
                self.logger.error(e)
                error_response = {"status": "error", "message": str(e)}
                client_socket.send(json.dumps(error_response).encode())
                break

        client_socket.close()

    def replicate(self, command):
        services = json.load(open("config.json"))['services']
        for service_id, service_prop in services.items():
            service_name = service_prop['name']
            service_port = service_prop['replication_port']
            if service_id != Context.get_id():
                self.logger.info(
                    f"Replicating to {service_name}:{service_port} from {Context.get_id()}")

                self.database_client.execute(service_name, int(service_port), command['query'])
                self.logger.info(
                    f"Successfully replicated to {service_name}:{service_port} from {Context.get_id()}")

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
