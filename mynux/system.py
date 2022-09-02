from typing import Dict

from logging import getLogger
from pathlib import Path

from .storage import load_local
from .storage.plain import ActionCls
from .utils import FileOperation, load_toml

logger = getLogger(__name__)


class SysStorage(ActionCls):
    """
    This is the multi storage, that include multiple storage on the system.
    """

    SYS_CONFIG_PATH: Path = Path("/etc/mynux/config.toml")
    USER_CONFIG_PATH: Path = Path("~/.config/mynux/config.toml").expanduser()

    DEFAULT_SYS_DOTFILES: Path = Path("/etc/mynux/dotfiles")
    DEFAULT_USER_DOTFILES: Path = Path("~/.config/mynux/dotfiles").expanduser()

    DEFAULT_USER_GIT_DIR: Path = Path("~/.config/mynux/repos/git").expanduser()

    DEFAULT_ACTIONS = {"info": False, "file": ["target_dir", "default_file_operation"]}

    def __init__(self, path: Path | None = None, load_sys_conf: bool = True, load_user_conf: bool = True):
        super().__init__()
        self.config: Dict = {}
        if load_sys_conf:
            self._update_conf(self.SYS_CONFIG_PATH)
        if load_user_conf:
            self._update_conf(self.USER_CONFIG_PATH)
        if path:
            self._update_conf(path.resolve())

    def _update_conf(self, path: Path) -> None:
        data = load_toml(path)
        self.config.update(data)

    def action_info(self) -> bool:
        for storage in self.iter_storage():
            print("storage", storage)
            storage.action_info()
        return True

    def action_file(self, target_dir=Path.home(), default_file_operation: FileOperation = FileOperation.LINK) -> bool:
        for storage in self.iter_storage():
            storage.action_file(target_dir, default_file_operation)
        return True

    def iter_storage(self):
        if storage := load_local(self.config.get("system", {}).get("dotfiles") or self.DEFAULT_SYS_DOTFILES):
            yield storage
        if storage := load_local(self.config.get("user", {}).get("dotfiles") or self.DEFAULT_USER_DOTFILES):
            yield storage

        repos_git: Path = self.config.get("user", {}).get("git_dir") or self.DEFAULT_USER_GIT_DIR
        if repos_git.is_dir():
            for path in repos_git.iterdir():
                if storage := load_local(path):
                    yield storage

    def iter_files(self, target_dir: Path | None = None):
        """
        iterate source files (and target files)
        """
        for storage in self.iter_storage():
            yield from storage.iter_files(target_dir)
