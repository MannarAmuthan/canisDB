import logging
import threading

from db.server import DatabaseServer
from db.wal_logger import WALLogger


class Application:

    def __init__(self,
                 logger: logging.Logger,
                 database_server: DatabaseServer,
                 write_ahead_logger: WALLogger):
        self.logger: logging.Logger = logger
        self.database_server: DatabaseServer = database_server
        self.write_ahead_logger: WALLogger = write_ahead_logger

        self.database_server_thread = threading.Thread(target=self.database_server.start,
                                                       args=())

    def start(self):
        self.logger.info("Starting database servers")

        self.database_server_thread.start()

        self.write_ahead_logger.init_logger()

        self.logger.info("Started database servers")

    def stop(self):
        self.database_server.stop()
        self.database_server_thread.join()
