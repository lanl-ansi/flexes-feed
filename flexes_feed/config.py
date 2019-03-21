import json
import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

def load_config(config_path=None):
    """Load the configuration for the data feed components. The configuration loader 
    will override values defined in the library's `default_config.json` file with 
    values defined in the `config_path` argument. By default this file is located in 
    the current working directory and named `config.json`
    
    Args:
        config_path (str): Path to the user defined configuration variables. These 
            variables will override the library's default configuration values. The 
            default configuration path is `./config.json`.

    Returns:
        dict: A dictionary containing configuration variables
    """
    default = PACKAGE_DIR.joinpath('default_config.json')
    with default.open() as f:
        config = json.load(f)

    user_config = Path(config_path) if config_path is not None else PACKAGE_DIR.joinpath('config.json')
    if user_config.exists():
        with user_config.open() as f:
            user = json.load(f)

        for key, value in user.items():
            config[key] = value

    return config
