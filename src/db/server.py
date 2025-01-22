import json
import socket
import threading
from logging import Logger

from context import Context
from db.connector import DBConnector
from db_logger import QueryLoggerFactory, WriteLoggerFactory
from db.client import DatabaseClient
from sql.classifier import is_write_operation
from sql.transformer import transform_sql_query
from vars import DEFAULT_DATABASE_REPLICATION_PORT


class DatabaseServer:
    def __init__(self,
                 host,
                 port: int,
                 logger: Logger,
                 is_replication_server: bool,
                 database_client: DatabaseClient,
                 db_connector: DBConnector):
        self.host = host
        self.port = port
        self.logger: Logger = logger
        self.is_replication_server = is_replication_server
        self.database_client = database_client

        self.transaction_logger = QueryLoggerFactory.get_logger()
        self.write_logger = WriteLoggerFactory.get_logger()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.db_connector = db_connector

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

                if not self.is_replication_server:
                    command['query'] = transform_sql_query(command['query'])

                self.transaction_logger.info(msg=command)

                if is_write_operation(command['query']):
                    self.logger.info("Logging into Write Logs")
                    self.write_logger.info(msg=command)

                    if not self.is_replication_server:
                        self.replicate(command)

                response = self.db_connector.execute_query(command)

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
            service_port = DEFAULT_DATABASE_REPLICATION_PORT
            if service_id != Context.get_id():
                self.logger.info(
                    f"Replicating to {service_name}:{service_port} from {Context.get_id()}")

                self.database_client.execute(service_name, int(service_port), command['query'], command['params'])
                self.logger.info(
                    f"Successfully replicated to {service_name}:{service_port} from {Context.get_id()}")
