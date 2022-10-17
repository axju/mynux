import sys
from logging import getLogger

from mynux.system import SysStorage
from mynux.utils import get_mynux_arg_parser

logger = getLogger(__name__)


def main(*argv: str) -> int:
    logger.info("run info with: %s", argv)
    parser = get_mynux_arg_parser(prog="add")
    parser.add_argument("-s", "--system", action="store_true", help="add to system storage dir")
    parser.add_argument("-d", "--dir", type=str, help="set directory name")
    parser.add_argument("source", type=str, help="source path/url")

    args = parser.parse_args(argv)
    storage = SysStorage.create()
    result = storage("add", source=args.source, system=args.system, dir_name=args.dir)
    return 1 if result is None else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
