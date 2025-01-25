import logging
import threading

from db.server import DatabaseServer
from db.wal_logger import WALLogger
from gossip import GossipService


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

        self.database_server_thread = threading.Thread(target=self.database_server.start,
                                                       args=())

        self.internal_listener_thread = threading.Thread(target=self.gossip_service.start,
                                                    args=())

    def start(self):
        self.logger.info("Starting database servers")

        self.database_server_thread.start()
        self.internal_listener_thread.start()

        self.write_ahead_logger.init_logger()

        self.logger.info("Started database servers")

    def stop(self):
        self.database_server.stop()
        self.database_server_thread.join()


