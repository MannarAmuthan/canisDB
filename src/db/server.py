import abc

import socket
import threading
from logging import Logger

from db.connector import DBConnector
from db.wal_logger import WALLogger
from db_logger import QueryLoggerFactory, WriteLoggerFactory
from db.client import DatabaseClient


class DatabaseServer:
    def __init__(self,
                 host,
                 port: int,
                 logger: Logger,
                 is_leader: bool,
                 database_client: DatabaseClient,
                 db_connector: DBConnector):
        self.host = host
        self.port = port
        self.logger: Logger = logger
        self.is_leader = is_leader
        self.database_client = database_client

        self.transaction_logger = QueryLoggerFactory.get_logger()
        self.write_logger = WriteLoggerFactory.get_logger()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.db_connector = db_connector

        self.wal_logger = WALLogger(self.db_connector)

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

    def stop(self):
        self.logger.info(f"Stopping server")
        self.socket.close()

    @abc.abstractmethod
    def handle_client(self, client_socket: socket.socket):
        pass
