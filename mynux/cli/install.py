import sys
from logging import getLogger
from pathlib import Path

from mynux.storage import load
from mynux.system import SysStorage
from mynux.utils import get_mynux_arg_parser

logger = getLogger(__name__)


def parse_args(*argv: str):
    parser = get_mynux_arg_parser(prog="install")
    parser.add_argument("-t", "--target", type=Path, default=Path.home(), help="Target directory, default='~'")
    parser.add_argument("-a", "--action", type=str, choices=["file", "pkgs", "info"], help="Just run a single action.")
    parser.add_argument("-s", "--skip_add", action="store_true", help="Do not add storage to storage directory.")
    parser.add_argument("source", nargs="?", type=str, help="source dir")
    return parser, parser.parse_args(argv)


def load_storage(source: str, skip_add: bool = False):
    if skip_add:
        return load(source)
    sys_storage = SysStorage.create()
    return sys_storage("add", source=source, system=False)


def main(*argv: str) -> int:
    logger.info("run install with: %s", argv)
    _, args = parse_args(*argv)

    if args.source is not None:
        storage = load_storage(args.source)

        if storage is None:
            logger.error('Fail to load storage "%s".', args.source)
            return 1
    else:
        storage = SysStorage.create()

    match args.action:
        case "file":
            kwargs = {"target_dir": args.target}
        case None:
            kwargs = {"target_dir": args.target}
        case _:
            kwargs = {}

    if storage is not None and storage(args.action, **kwargs):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
