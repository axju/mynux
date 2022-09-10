import sys
from logging import getLogger

from mynux.storage import load as load_storage
from mynux.utils import get_mynux_arg_parser

logger = getLogger(__name__)


def main(*argv: str) -> int:
    logger.info("run info with: %s", argv)
    parser = get_mynux_arg_parser(prog="add")
    parser.add_argument("source", type=str, help="source path/url")

    args = parser.parse_args(argv)
    storage = load_storage(args.source)
    print(storage)
    return 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
