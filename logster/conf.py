import json
import os

from . import base_dir


config = None

if config is None:
    config_path = os.path.join(base_dir, 'config.json')

    with open(config_path, 'r') as f:
        config = json.load(f)
