import json
import os

from . import base_dir


config = None

if config is None:
    config_path = os.path.join(base_dir, 'config.json')

    with open(config_path, 'r') as f:
        config = json.load(f)

# Logging configuration
app, scanner = config['app'], config['scanner']

logging_conf = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '[%(asctime)s - %(levelname)s - %(module)s] %(message)s',
        },
    },

    'handlers': {
        'webapp_log_file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': app.get(
                'logPath', os.path.join(base_dir, 'logster.log')
            ),
            'level': app.get('logLevel', 'INFO'),
        },
        'scanner_log_file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': scanner.get(
                'logPath', os.path.join(base_dir, 'logster_scanner.log')
            ),
            'level': scanner.get('logLevel', 'INFO'),
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },

    'loggers': {
        'webapp': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['webapp_log_file', 'console'],
        },
        'scanner': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['scanner_log_file', 'console'],
        },
    },
}
