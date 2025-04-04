import datetime
import json
import socket
from logging import Logger

from db.connector import DBConnector
from db.server import DatabaseServer
from db.client import DatabaseClient
from sql.classifier import is_write_operation
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

                is_coming_from_leader = command.get('replicaRequest', None)
                is_commit_request = command.get('isCommitRequest', False)
                is_prepare_request = not is_commit_request
                write_operation = is_write_operation(command['query']) if 'query' in command else False

                should_redirect_to_leader = write_operation and not is_coming_from_leader

                if should_redirect_to_leader:
                    service_name, service_port = self.get_leader_service_details()
                    self.logger.info("Submitting the query to leader")
                    response = self.database_client.execute(service_name,
                                                            service_port,
                                                            command
                                                            )
                elif write_operation and is_prepare_request:
                    self.logger.info(f"Applying prepare for {command.get('unique_id')}")
                    response = self.raft_log.prepare(
                        unique_id=command.get('unique_id'),
                        log_date=datetime.datetime.now(),
                        command=command
                    )
                elif is_commit_request:
                    self.logger.info(f"Applying commit for {command.get('unique_id')}")
                    response = self.raft_log.commit(
                        unique_id=command.get('unique_id'),
                        commit_date=datetime.datetime.now()
                    )
                else:
                    response = self.db_connector.execute_query(command)

                client_socket.send(json.dumps(response).encode())

            except Exception as e:
                self.logger.error("Error in connecting")
                self.logger.error(e)
                error_response = {"status": "error", "message": str(e)}
                client_socket.send(json.dumps(error_response).encode())
                break

        client_socket.close()

    def get_leader_service_details(self):
        services = json.load(open("config.json"))['services']
        for service_id, service_prop in services.items():
            service_name = service_prop['name']
            service_port = DEFAULT_DATABASE_SERVER_PORT
            if service_prop.get('leader', None):
                return service_name, int(service_port)

        self.logger.error("Could not find leader details")
        raise Exception("Could not find leader details")
