import os


base_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))  


def setup_logging():
    logging.config.dictConfig(logging_conf)