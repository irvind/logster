import logging.config

from .conf import logging_conf


def setup_logging():
    logging.config.dictConfig(logging_conf)
