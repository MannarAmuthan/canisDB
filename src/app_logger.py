import logging
import sys

from context import Context


class LoggerFactory:
    _logger: logging.Logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger(f'canis-{Context.get_id()}')
            cls._logger.setLevel(logging.DEBUG)

            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S'
            ))

            cls._logger.addHandler(handler)

        return cls._logger
