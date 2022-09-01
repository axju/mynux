import sys
from logging import getLogger

from mynux.storage import load
from mynux.utils import get_mynux_arg_parser

logger = getLogger(__name__)


def main(*argv: str) -> int:
    logger.info("run info with: %s", argv)
    parser = get_mynux_arg_parser(prog="info")
    parser.add_argument("source", type=str, help="source dir")

    args = parser.parse_args(argv or sys.argv)
    storage = load(args.source)
    if storage is None:
        logger.error('Fail to load storage "%s".', args.source)
        return 1
    return int(storage.action("info"))


if __name__ == "__main__":
    sys.exit(main())
