import datetime
import json
import socket
from logging import Logger

from context import Context
from db.connector import DBConnector
from db.server import DatabaseServer
from db.client import DatabaseClient
from sql.classifier import is_write_operation
from sql.transformer import transform_sql_query
from vars import DEFAULT_DATABASE_SERVER_PORT


class Leader(DatabaseServer):
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

                if self.is_leader:
                    command['query'] = transform_sql_query(command['query'])

                self.transaction_logger.info(msg=command)

                if is_write_operation(command['query']):
                    self.logger.info("Logging into Write Logs")
                    self.write_logger.info(msg=command)
                    self.wal_logger.log(datetime.datetime.now(), command)

                    if self.is_leader:
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
            service_port = DEFAULT_DATABASE_SERVER_PORT
            if service_id != Context.get_id():
                self.logger.info(
                    f"Replicating to {service_name}:{service_port} from {Context.get_id()}")

                command = {
                    "query": command['query'],
                    "params": command['params'] if command['params'] else [],
                    "replicaRequest": True
                }

                self.database_client.execute(service_name, int(service_port), command)
                self.logger.info(
                    f"Successfully replicated to {service_name}:{service_port} from {Context.get_id()}")
