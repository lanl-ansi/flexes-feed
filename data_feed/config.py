import json
import os
from pathlib import Path

def load_config(config_path='config.json'):
    default_path = os.path.join(os.path.dirname(__file__), 'default_config.json')
    default = Path(default_path)
    with default.open() as f:
        config = json.load(f)

    user_config = Path(config_path)
    if user_config.exists():
        with user_config.open() as f:
            user = json.load(f)

        for key, value in user.items():
            config[key] = value

    return config
