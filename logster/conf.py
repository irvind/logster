import json
import os

from . import base_dir


config = None

if config is None:
    config_path = os.path.join(base_dir, 'config.json')

    with open(config_path, 'r') as f:
        config = json.load(f)

# Logging configuration
log_path = config['app'].get('logPath', os.path.join(base_dir, 'logster.log'))
log_level = config['app'].get('logLevel', 'INFO')

logging_conf = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '[%(asctime)s - %(levelname)s - %(module)s] %(message)s',
        },
    },

    'handlers': {
        'main_log_file': {
            'class': 'logging.FileHandler',
            'filename': log_path,
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['main_log_file', 'console'],
    },
}
