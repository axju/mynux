import sys
from logging import getLogger
from pathlib import Path

from mynux.storage import load
from mynux.system import SysStorage
from mynux.utils import get_mynux_arg_parser

logger = getLogger(__name__)


def parse_args(*argv: str):
    parser = get_mynux_arg_parser(prog="install")
    parser.add_argument("-t", "--target", type=Path, default=Path.home(), help='target dir, default="~"')
    parser.add_argument("-a", "--action", type=str, choices=["file", "pkgs", "info"], help="just run a single action")
    parser.add_argument("source", nargs="?", type=str, help="source dir")
    return parser, parser.parse_args(argv)


def main(*argv: str) -> int:
    logger.info("run install with: %s", argv)
    _, args = parse_args(*argv)

    storage = load(args.source) or SysStorage()
    if storage is None:
        logger.error('Fail to load storage "%s".', args.source)
        return 1

    match args.action:
        case "file":
            kwargs = {"target_dir": args.target}
        case None:
            kwargs = {"target_dir": args.target}
        case _:
            kwargs = {}

    if storage.action(args.action, **kwargs):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
