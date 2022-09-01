import sys
from argparse import REMAINDER, SUPPRESS, ArgumentParser
from logging import basicConfig, getLogger

from mynux import __version__, cmds

logger = getLogger(__name__)


def help_cmds():
    width = max(map(len, cmds.keys()))
    for name, cmd in cmds.items():
        func = cmd.load()
        help_str = func.__doc__ or ""
        print(f"{name:>{width}} --> {help_str}")


def main_parse_args(argv=None):
    parser = ArgumentParser()
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-v", "--verbose", action="count", help="verbose level... repeat up to three times")
    parser.add_argument("-H", "--help_cmds", action="store_true", help="some command info")
    parser.add_argument("cmd", nargs="?", choices=cmds.keys(), help="select one command")
    parser.add_argument("args", help=SUPPRESS, nargs=REMAINDER)
    return parser, parser.parse_args(argv)


def main(argv=None):
    parser, args = main_parse_args(argv)

    if args.verbose:
        level = 40 - args.verbose * 10 if args.verbose <= 3 else 30
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        basicConfig(level=level, format=log_format)

    if args.help_cmds:
        return help_cmds()

    if args.cmd:
        try:
            func = cmds[args.cmd].load()
            sys.exit(func(*args.args))
        except Exception as exc:
            if args.verbose:
                raise
            logger.error('Oh no, a error :(\nError: "%s"', exc)
            logger.error("Run with --verbose for more information.")
            sys.exit(1)

    sys.exit(parser.print_help())


if __name__ == "__main__":
    main()
