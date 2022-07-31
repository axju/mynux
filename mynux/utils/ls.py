"""Tools for iterat the files"""
from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser
from mynux.dots import DotDir


logger = getLogger(__name__)


def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='ls')
    parser.add_argument('source', type=Path, help='source dir')
    return parser, parser.parse_args(argv)


def cli(*argv) -> None:
    """just link some files"""
    logger.info('run clinkopy with: %s', argv)

    parser, args = parse_args(*argv)
    dotdir = DotDir(args.source)
    for pkg in dotdir.iter_pkg():
        print(pkg)


if __name__ == '__main__':
    cli()