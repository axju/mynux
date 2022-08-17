from pathlib import Path
from configparser import ConfigParser


DEFAULT_CONFIG = {
    'root': {
        'RepoDir': '/etc/mynux/repos',
        'DotFiles': '/etc/mynux/dotfiles',
    },
    'system': {
        'Path': '/etc/mynux/dotfiles',
    },
    'local': {
        'Path': '~./config/mynux/dotfiles',
    },
}

DEFAULT_CONFIG_PATH: Path = Path('/etc/mynux/config.ini')


def get_default_config() -> ConfigParser:
    config = ConfigParser()
    for key, value in DEFAULT_CONFIG.items():
        config[key] = value
    return config


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    config = get_default_config()
    config.read(path)
    return {key: dict(config.items(key)) for key in config.sections()}


def create_default_config(path: Path = DEFAULT_CONFIG_PATH):
    config = get_default_config()
    with path.open('w') as file:
        config.write(file)
