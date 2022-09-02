import sys
from logging import getLogger

from mynux.system import SysStorage
from mynux.utils.__init__ import get_mynux_arg_parser

from ..storage import load

logger = getLogger(__name__)


def main(*argv: str) -> int:
    logger.info("run info with: %s", argv)
    parser = get_mynux_arg_parser(prog="info")
    parser.add_argument("source", nargs="?", type=str, help="source dir")

    args = parser.parse_args(argv)
    storage = load(args.source) or SysStorage()
    return int(storage.action("info"))


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
