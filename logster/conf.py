import json
import os


config = None

if config is None:
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '../config.json'
    )

    with open(config_path, 'r') as f:
        config = json.load(f)
