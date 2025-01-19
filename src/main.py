import argparse
import logging
import threading
from pathlib import Path

from context import Context
from db_server.client import DatabaseClient
from db_server.server import DatabaseServer
from app_logger import LoggerFactory

DEFAULT_DATABASE_SERVER_PORT = 5012
DEFAULT_DATABASE_REPLICATION_PORT = 5022
GRPC_SERVER_PORT = 50051


class Application:

    def __init__(self,
                 logger: logging.Logger,
                 primary_server: DatabaseServer,
                 replication_server: DatabaseServer):
        self.logger: logging.Logger = logger
        self.primary_server = primary_server
        self.dp_replication_server = replication_server

    def start(self):
        self.logger.info("Starting database servers")

        database_server_thread = threading.Thread(target=self.primary_server.start,
                                                  args=())
        database_server_thread.start()

        database_replication_thread = threading.Thread(target=self.dp_replication_server.start,
                                                       args=())
        database_replication_thread.start()

        self.logger.info("Started database servers")


def initialize_and_get_configurations(parsed_args):
    Context.set_id(parsed_args.id)
    Context.set_folder(f"{parsed_args.folder}/{parsed_args.id}" if parsed_args.folder else f"local/{parsed_args.id}")

    Path(Context.get_folder()).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port')
    parser.add_argument('-id', '--id')

    parser.add_argument('-fo', '--folder')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    initialize_and_get_configurations(args)

    logger_instance: logging.Logger = LoggerFactory.get_logger()
    database_client: DatabaseClient = DatabaseClient(logger_instance)

    primary_server_instance: DatabaseServer = DatabaseServer(
        host='0.0.0.0',
        port=DEFAULT_DATABASE_SERVER_PORT,
        logger=logger_instance,
        is_replication_server=False,
        database_client=database_client)

    dp_replication_server_instance: DatabaseServer = DatabaseServer(
        host='0.0.0.0',
        port=DEFAULT_DATABASE_REPLICATION_PORT,
        logger=logger_instance,
        is_replication_server=True,
        database_client=database_client)

    application = Application(logger=logger_instance,
                              primary_server=primary_server_instance,
                              replication_server=dp_replication_server_instance)
    application.start()
