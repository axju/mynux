import shutil
from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser
from mynux.config import DEFAULT_CONFIG_PATH, load_config

logger = getLogger(__name__)


def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='mynux cp')
    parser.add_argument(
        '-s', '--settings', type=Path, default=DEFAULT_CONFIG_PATH,
        help='setting file, default="/etc/mynux/settings.conf"'
    )
    return parser, parser.parse_args(argv)


def run(config_path: Path=DEFAULT_CONFIG_PATH) -> None:
    """
    Main function.
    Settings are in /etc/mynux/settings.conf
    """
    logger.info('load settings "%s"', config_path)
    config = load_config(config_path)
    print(config)


def cli(*argv):
    """just copy some files"""
    parser, args = parse_args(*argv)
    run(args.settings)
    

if __name__ == '__main__':
    cli()