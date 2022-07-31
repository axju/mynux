from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser, ask_to_confirm
from mynux.config import DEFAULT_CONFIG_PATH, create_default_config

logger = getLogger(__name__)


def init(config_path: Path=DEFAULT_CONFIG_PATH):
    if config_path.is_file() and ask_to_confirm(f'Config file ({config_path}) alrady exist, overrwirte file?', default=False):
        try:
            create_default_config(config_path)
        except PermissionError:
            print('try "sudo !!"')


def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='init')
    parser.add_argument(
        '-p', '--path', type=Path, default=DEFAULT_CONFIG_PATH,
        help=f'config path, default="{DEFAULT_CONFIG_PATH}"'
    )
    return parser, parser.parse_args(argv)


def cli(*argv):
    """just init mynux"""
    parser, args = parse_args(*argv)
    init(args.path)
    

if __name__ == '__main__':
    cli()