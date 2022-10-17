from typing import Dict

import os
from logging import getLogger
from pathlib import Path
from shutil import copytree

from .storage import Storage, iter_storage_dir
from .storage import load as auto_load_storage
from .storage import load_local
from .utils import FileOperation, load_toml
from .utils.action import ActionCls

logger = getLogger(__name__)


class SysStorage(ActionCls):
    """
    This is the multi storage, that include multiple storage on the system.
    """

    SYS_CONFIG_PATH: Path = Path("/etc/mynux/config.toml")
    USER_CONFIG_PATH: Path = Path("~/.config/mynux/config.toml").expanduser()

    DEFAULT_SYS_STORAGE_DIR: Path = Path("/usr/share/mynux/storage/")
    DEFAULT_USER_STORAGE_DIR: Path = Path("~/.config/mynux/storage/").expanduser()

    DEFAULT_ACTIONS = {
        "info": False,
        "file": ["target_dir", "default_file_operation"],
        "pkgs": True,
    }

    def __init__(self, path: Path | None = None, load_sys_conf: bool = True, load_user_conf: bool = True):
        super().__init__()
        self.config: Dict = {}
        if load_sys_conf:
            self._update_conf(self.SYS_CONFIG_PATH)
        if load_user_conf:
            self._update_conf(self.USER_CONFIG_PATH)
        if path:
            self._update_conf(path.resolve())

        self.sys_storage_dir = self.config.get("system", {}).get("storage") or self.DEFAULT_SYS_STORAGE_DIR
        self.user_storage_dir = self.config.get("user", {}).get("storage") or self.DEFAULT_USER_STORAGE_DIR

    def __str__(self):
        return "SystemStorage"

    @classmethod
    def create(cls, **kwargs):
        """
        Create system Storage, arguments could be load by environment variables.
        """
        path = kwargs.get("path") or os.environ.get("mynux_conf")
        if isinstance(path, (str, Path)):
            path = Path(path).resolve()
        else:
            path = None
        load_sys_conf: bool = True
        load_user_conf: bool = True
        return cls(path, load_sys_conf, load_user_conf)

    def _update_conf(self, path: Path) -> None:
        data = load_toml(path)
        self.config.update(data)

    def action_info(self) -> bool:
        for storage in self.iter_storage():
            print("*" * 65)
            storage.action_info()
        return True

    def action_file(self, target_dir=Path.home(), default_file_operation: FileOperation = FileOperation.COPY) -> bool:
        for storage in self.iter_storage():
            logger.info("action file for storage: %s", storage)
            storage("file", target_dir=target_dir, default_file_operation=default_file_operation)
        return True

    def action_pkgs(self) -> bool:
        for storage in self.iter_storage():
            logger.info("action pkgs for storage: %s", storage)
            storage("pkgs")
        return True

    def action_add(self, source: str, system: bool = False, dir_name: str | None = None) -> Storage | None:
        """Add storage to locale system.
        Args:
            source (str): Source string to load storage.
            system (bool): true -> Install to system directory, false install to home directory. Default=False
            dir_name (str): name for storage directory. Default=None

        Return:
            Storage | None: If storage already exist, return found storage. None if Storage can not load.
        """
        storage_dir: Path = self.sys_storage_dir if system else self.user_storage_dir
        storage_target: Path | None = None

        if dir_name:
            storage_target = storage_dir / dir_name
            if storage_target.is_dir():
                logger.warning("Storage directory already exist! Try other name.")
                return None

        storage_tmp = auto_load_storage(source)
        if not storage_tmp:
            logger.warning("Source string '%s' can not load", source)
            return None

        for storage in iter_storage_dir(storage_dir):
            if storage == storage_tmp:
                logger.warning("Storage already exist.")
                return storage

        if storage_target is None:
            storage_target = storage_dir / storage_tmp.get_name()
            if storage_target.is_dir():
                storage_target = storage_dir / storage_tmp.path.name
        logger.info("Install new storage to '%s'", storage_target)
        copytree(str(storage_tmp), str(storage_target))
        return load_local(storage_target)

    def iter_storage(self):
        yield from iter_storage_dir(self.sys_storage_dir)
        yield from iter_storage_dir(self.user_storage_dir)

    def iter_files(self, target_dir: Path | None = None):
        """
        iterate source files (and target files)
        """
        for storage in self.iter_storage():
            yield from storage.iter_files(target_dir)
