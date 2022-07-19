from pathlib import Path
from logging import getLogger, StreamHandler, Formatter, WARNING, INFO, DEBUG
from argparse import ArgumentParser
from subprocess import Popen, PIPE


logger = getLogger()

default_paths = [
    '~/.dotfiles',
    '~/.dotfiles/src',
    '~/.dotfile',
    '~/.dotfile/src',
    '~/.dots',
    '~/.dots/src',
]


def setup_logger(level=0, root='', format_str='%(asctime)s - %(levelname)-7s - %(message)s'):
    """setup the root logger"""
    levels = [WARNING, INFO, DEBUG]
    level = levels[min(len(levels) - 1, level or 0)]
    local_logger = getLogger(root)
    local_logger.setLevel(level)
    ch = StreamHandler()
    ch.setFormatter(Formatter(format_str))
    ch.setLevel(level)
    local_logger.addHandler(ch)
    return local_logger


def check_local_path(path):
    path = Path(path)
    if path.is_dir() and Path(path / 'mynux.py').is_file():
        return path
    if path.is_file() and path.name == 'mynux.py':
        return path.parent
    return False


def get_local_path(path):
    logger.debug('path in "%s"', path)
    if path is None:
        logger.debug('no path, try to finde default')
        for default in map(lambda p: Path(p).expanduser(), default_paths):
            if check_local_path(default):
                logger.info('no path, take default path "%s"', default)
                return default
    return check_local_path(path)


def get_git_path(path):
    result = Popen(['git', '-C', path, 'rev-parse', '2>/dev/null'], stdout=PIPE, stderr=PIPE)
    result.communicate()[0]
    print(result.returncode)


def main():
    default_dir = Path.home() / '.dotfils'
    parser = ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='count', 
        help="verbose level... repeat up to three times"
    )
    parser.add_argument(
        'path', nargs='?',
        help="path to dotfiles or git repo"
    )
    args = parser.parse_args()
    setup_logger(args.verbose)
    path = get_local_path(args.path)
    if not isinstance(path, Path):
        path = get_git_path(args.path)


if __name__ == '__main__':
    main()


# def link_path(path, src_dir):
#     path = Path(path)
#     target = Path.home() / path.relative_to(src_dir)
    
#     logger.debug('file:   "%s"', path)
#     logger.debug('target: "%s"', target)
#     logger.debug('='*42)
    
#     if target.is_file():
#         logger.warning('delete existing file')
#         target.unlink()
#     elif target.is_symlink():
#         logger.warning('unlink existing link')
#         target.unlink()

#     target.parent.mkdir(parents=True, exist_ok=True)
#     target.symlink_to(path)


# def main(src_dir=Path(__file__).parent.parent / 'src'):
#     src_dir = Path(src_dir)
#     logger.debug('src:    "%s"', src_dir)

#     for path in src_dir.glob('**/*'):
#         if not path.is_file():
#             continue
#         if path.suffix in ['.pyc']:
#             continue
#         link_path(path, src_dir)