import argparse
import logging
import threading
from pathlib import Path

from context import Context
from db.client import DatabaseClient
from db.connector import DBConnector
from db.follower import Follower
from db.leader import Leader
from db.server import DatabaseServer
from app_logger import LoggerFactory
from db.wal_logger import WALLogger
from gossip import GossipService
from vars import DEFAULT_DATABASE_SERVER_PORT, LISTENER_PORT


class Application:

    def __init__(self,
                 logger: logging.Logger,
                 database_server: DatabaseServer,
                 internal_listener: GossipService,
                 write_ahead_logger: WALLogger):
        self.logger: logging.Logger = logger
        self.database_server: DatabaseServer = database_server
        self.gossip_service: GossipService = internal_listener
        self.write_ahead_logger: WALLogger = write_ahead_logger

    def start(self):
        self.logger.info("Starting database servers")

        database_server_thread = threading.Thread(target=self.database_server.start,
                                                  args=())
        database_server_thread.start()

        internal_listener_thread = threading.Thread(target=self.gossip_service.start,
                                                    args=())
        internal_listener_thread.start()

        self.write_ahead_logger.init_logger()
        self.logger.info("Started database servers")


def initialize_and_get_configurations(parsed_args):
    Context.set_id(parsed_args.id)
    Context.set_folder(f"{parsed_args.folder}/{parsed_args.id}" if parsed_args.folder else f"local/{parsed_args.id}")
    Context.set_role(parsed_args.role if parsed_args.role else "follower")
    Path(Context.get_folder()).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port')
    parser.add_argument('-id', '--id')

    parser.add_argument('-fo', '--folder')
    parser.add_argument('-r', '--role')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    initialize_and_get_configurations(args)

    logger_instance: logging.Logger = LoggerFactory.get_logger()
    database_client: DatabaseClient = DatabaseClient(logger_instance)

    db_connector: DBConnector = DBConnector(file_path=
                                            f'{Context.get_folder()}/database.db')

    if Context.get_role() == "leader":
        server_instance: DatabaseServer = Leader(
            host='0.0.0.0',
            port=DEFAULT_DATABASE_SERVER_PORT,
            logger=logger_instance,
            is_leader=True,
            database_client=database_client,
            db_connector=db_connector
        )

    else:
        server_instance: DatabaseServer = Follower(
            host='0.0.0.0',
            port=DEFAULT_DATABASE_SERVER_PORT,
            logger=logger_instance,
            is_leader=False,
            database_client=database_client,
            db_connector=db_connector)

    gossip_service: GossipService = GossipService(
        host='0.0.0.0',
        port=LISTENER_PORT,
        logger=logger_instance)

    wal_logger = WALLogger(database_connector=db_connector)

    application = Application(logger=logger_instance,
                              database_server=server_instance,
                              internal_listener=gossip_service,
                              write_ahead_logger=wal_logger)
    application.start()
