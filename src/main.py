import argparse
import logging
from pathlib import Path

from application import Application
from context import Context
from db.client import DatabaseClient
from db.connector import DBConnector
from db.follower import Follower
from db.leader import Leader
from db.server import DatabaseServer
from app_logger import LoggerFactory
from db.wal_logger import WALLogger
from vars import DEFAULT_DATABASE_SERVER_PORT


def initialize_and_get_configurations(parsed_args):
    Context.set_id(parsed_args.id)
    Context.set_folder(f"{parsed_args.folder}/{parsed_args.id}" if parsed_args.folder else f"local/{parsed_args.id}")
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

    if args.role and args.role == "leader":
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

    wal_logger = WALLogger(database_connector=db_connector)

    application = Application(logger=logger_instance,
                              database_server=server_instance,
                              write_ahead_logger=wal_logger)
    application.start()
