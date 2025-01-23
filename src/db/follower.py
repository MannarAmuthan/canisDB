import json
import socket
import threading
from logging import Logger

from context import Context
from db.connector import DBConnector
from db.server import DatabaseServer
from db_logger import QueryLoggerFactory, WriteLoggerFactory
from db.client import DatabaseClient
from sql.classifier import is_write_operation
from sql.transformer import transform_sql_query
from vars import DEFAULT_DATABASE_SERVER_PORT


class Follower(DatabaseServer):
    def __init__(self,
                 host,
                 port: int,
                 logger: Logger,
                 is_leader: bool,
                 database_client: DatabaseClient,
                 db_connector: DBConnector):
        super().__init__(host, port, logger, is_leader, database_client, db_connector)

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
                    self.logger.info("Logging into Write Logs")
                    self.write_logger.info(msg=command)

                response = self.db_connector.execute_query(command)

                client_socket.send(json.dumps(response).encode())

            except Exception as e:
                self.logger.error("Error in connecting")
                self.logger.error(e)
                error_response = {"status": "error", "message": str(e)}
                client_socket.send(json.dumps(error_response).encode())
                break

        client_socket.close()
