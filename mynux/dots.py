import re
import fnmatch
from typing import Optional
from pathlib import Path
from logging import getLogger
from importlib.util import spec_from_file_location, module_from_spec


logger = getLogger(__name__)


def check_filter(path, filters):
    """return True if som filter match"""
    for pattern in filters:
        if re.search(fnmatch.translate(pattern), str(path)):
            return True
    return False       


def iter_gitignore_filter(gitignore_path: Path):
    """load filters from gitignore"""
    if gitignore_path.is_file():
        with gitignore_path.open() as file:
            gitignore_filters = file.read().splitlines()
        for filter in gitignore_filters:
            if not filter or filter.startswith('#'):
                continue
            if filter in filters:
                continue
            yield filter


def iter_dotfiles(path: Path):
    """only files"""
    filters = load_filters(path)
    for file in path.glob('**/*'):
        if file.is_file() and not check_filter(file, filters):
            yield file.resolve()


def iter_files(source_dir: Path, target_dir: Path):
    """loop source and targtet files"""
    source_dir, target_dir = source_dir.resolve(), target_dir.resolve()
    for source_file in iter_dotfiles(source_dir):
        yield source_file, target_dir / source_file.relative_to(source_dir)


class DotDir:
    """just a wrapper for a dotfile dir"""

    def __init__(self, path: Path):
        self.logger = getLogger(f'{__name__}.{self.__class__.__name__}')
        self._load_mynux(path)
        
    def _load_mynux(self, path: Optional[Path]):
        """load mynux.py file to self.mynux"""
        if path is not None:
            self.path = path.resolve()
        mynux_file = self.path / 'mynux.py'
        spec = spec_from_file_location('mynux.py', mynux_file)
        self.mynux = module_from_spec(spec)
        spec.loader.exec_module(self.mynux)

    def get_post_install_actions(self, action):
        actions = getattr(self.mynux, 'post_install_actions', {})
        return actions.get(action, [])

    def iter_pkg(self):
        packages = []
        for attr in ['packages', 'pkgs']:
            for pkg in getattr(self.mynux, attr, []):
                yield pkg

    def iter_files(self, target_dir: Optional[Path]):
        if target_dir is None:
            for file in iter_dotfiles(self.path):
                yield file
        else:
            for source_file, target_file in iter_files(self.path, target_dir):
                yield source_file, target_file

    def iter_filter(self):
        filters = []
        # first load default filter and git ignore
        for filter in iter_gitignore_filter(path / '.gitignore'):
            if filter in filters:
                continue
            yield filter
        
        # filter from mynux.py
        for filter in getattr(self.mynux, 'filters', []):
            if filter in filters:
                continue
            yield filter
                