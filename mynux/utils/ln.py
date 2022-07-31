from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser
from mynux.dots import iter_files

logger = getLogger(__name__)


def link(source_dir, target_dir=Path.home()):
    for source_file, target_file in iter_files(source_dir, target_dir):
        logger.info('link file "%s" to "%s"', source_file, target_file)
        
        if target_file.is_file():
            logger.warning('delete existing file')
            target_file.unlink()
        elif target_file.is_symlink():
            logger.warning('unlink existing link')
            target_file.unlink()

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.symlink_to(source_file)


def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='ln')
    parser.add_argument(
        '-t', '--target', type=Path, default=Path.home(),
        help='target dir, default="~"'
    )
    parser.add_argument('source', type=Path, help='source dir')
    return parser, parser.parse_args(argv)


def cli(*argv):
    """just link some files"""
    logger.info('run clinkopy with: %s', argv)

    parser, args = parse_args(*argv)
    link(args.source, args.target)
    

if __name__ == '__main__':
    cli()