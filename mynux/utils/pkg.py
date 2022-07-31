import shutil
import subprocess
from pathlib import Path
from logging import getLogger

from mynux.utils import get_mynux_arg_parser, ask_to_confirm
from mynux.dots import DotDir

logger = getLogger(__name__)


def check_pkg(pkg):
    """return True if packag ist installed"""
    return subprocess.run(['pacman', '-Qn', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def install(source_dir: Path) -> None:
    dotdir = DotDir(source_dir)

    new_pkgs = []
    for pkg in dotdir.iter_pkg():
        if check_pkg(pkg):
            continue

        # check if pkg is a group
        process = subprocess.run(['pacman', '-Qg', pkg], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        group_pkg = [line.decode().split()[1] for line in process.stdout.splitlines()]
        if all(map(check_pkg, group_pkg)):
           continue
            
        new_pkgs.append(pkg)

    if new_pkgs and ask_to_confirm(f'Missing {len(new_pkgs)} packages. Install them? ', default=True):
        subprocess.run(['sudo', 'pacman', '-S', '--noconfirm'] + new_pkgs)

        logger.info('run post install cmds:')
        for pkg in new_pkgs:
            for cmd in dotdir.get_post_install_actions(pkg):
                try:
                    subprocess.run(cmd.split())
                except:
                    logger.error('Fail cmdn "%s"', cmd)



def parse_args(*argv):
    parser = get_mynux_arg_parser(prog='pkg')
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
    install(source_dir=args.source)
    

if __name__ == '__main__':
    cli()