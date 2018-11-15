import json
import os
from pathlib import Path

def load_config(config_path='config.json'):
    """Load the configuration for the data feed components. The configuration loader 
    will override values defined in the library's `default_config.json` file with 
    values defined in the `config_path` argument. By default this file is located in 
    the current working directory and named `config.json`
    
    Args:
        config_path (str): Path to the user defined configuration variables. These 
            variables will override the library's default configuration values. The 
            default configuration path is `./config.json`.
    """
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
