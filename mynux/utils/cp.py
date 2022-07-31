import shutil
from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser, ask_to_confirm
from mynux.utils.ls import iter_files

logger = getLogger(__name__)


def copy(source_dir: Path, action: str='ask', target_dir: Path=Path.home()) -> None:
    for source_file, target_file in iter_files(source_dir, target_dir):

        if action == 'ask' and target_file.is_file() and not ask_to_confirm(f'File "{source_file}" alrady exist, overrwirte file?', default=True):
            print('skipp file')
            continue
        elif action == 'skipp' and target_file.is_file():
            print('skipp file')
            continue
        elif action not in ['ask', 'skipp', 'overwrite']:
            print('skipp file')
            continue

        logger.info('copy file "%s" to "%s"', source_file, target_file)
        target_file.unlink(missing_ok=True)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source_file, target_file)


def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='cp')
    parser.add_argument(
        '-t', '--target', type=Path, default=Path.home(),
        help='target dir, default="~"'
    )
    parser.add_argument(
        '-y', '--yes', action='store_true',
        help='always yes, overwrite all files'
    )
    parser.add_argument('source', type=Path, help='source dir')
    return parser, parser.parse_args(argv)


def cli(*argv):
    """just copy some files"""
    logger.info('run copy with: %s', argv)

    parser, args = parse_args(*argv)
    action = 'overwrite' if args.yes else 'ask'
    copy(source_dir=args.source, action=action, target_dir=args.target)
    

if __name__ == '__main__':
    cli()