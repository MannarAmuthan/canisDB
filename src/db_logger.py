import logging

from context import Context


class QueryLoggerFactory:
    _logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger(f'canis-db-{Context.get_id()}')
            cls._logger.setLevel(logging.DEBUG)

            # Add a file handler specific to QueryLogger
            handler = logging.FileHandler(Context.get_folder() + "/transaction_logs.txt", mode='a')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S'
            ))
            cls._logger.addHandler(handler)

        return cls._logger


class WALLoggerFactory:
    _logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger(f'canis-wal-db-{Context.get_id()}')
            cls._logger.setLevel(logging.DEBUG)

            # Add a file handler specific to WALLogger
            handler = logging.FileHandler(Context.get_folder() + "/wal_logs.txt", mode='a')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S'
            ))
            cls._logger.addHandler(handler)

        return cls._logger