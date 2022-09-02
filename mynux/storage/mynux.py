from typing import Dict, Iterable, List

import subprocess  # nosec
from enum import Enum
from logging import getLogger
from pathlib import Path

from mynux.utils import FileOperation, ask_to_confirm, check_pkg, file_operation_main, load_toml

from .plain import Storage

logger = getLogger(__name__)


class IterPkgAction(Enum):
    ALL = 1
    INSTALLED = 2
    NEW = 3


class MynuxStorage(Storage):
    DEFAULT_ACTIONS = {
        "info": False,
        "file": ["target_dir", "file_operation"],
        "pkgs": True,
    }
    DEFAULT_MYNUX_PATH_NAME: str = "mynux.toml"

    def __init__(self, path: Path):
        super().__init__(path)
        self.mynux_path: Path = path / self.DEFAULT_MYNUX_PATH_NAME
        self.mynux: Dict = load_toml(self.mynux_path)

    def __bool__(self):
        return self.mynux_path.is_file()

    def action_file(self, target_dir=Path.home(), default_file_operation: FileOperation = FileOperation.LINK) -> bool:
        for source_file, target_file in self.iter_files(target_dir):
            relative_source_file = source_file.relative_to(self.path)
            file_operation_str = self.mynux.get("files", {}).get(str(relative_source_file), "none")
            file_operation = FileOperation.get_from_str(file_operation_str, default_file_operation)
            if not file_operation_main(source_file, target_file, file_operation):
                return False
        return True

    def action_pkgs(self) -> bool:
        """
        install the packages from the mynux.toml file
        """
        logger.info("Load new package list.")
        pkgs = list(self.iter_pkgs(IterPkgAction.NEW))
        if pkgs and ask_to_confirm(f"Missing {len(pkgs)} packages. Install them? ", default=True):
            proc = subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + pkgs)  # nosec
            if proc.returncode != 0:
                logger.error("Fail to install packages! Check your mynux.toml file.")
                return False
            for pkg in pkgs:
                logger.info('Run post install cmds for "%s"', pkg)
                for cmd in self.iter_post_install_cmds(pkg):
                    try:
                        subprocess.run(cmd.split())  # nosec
                    except Exception as exc:
                        logger.exception('Fail cmd "%s"', cmd, exc_info=exc)
                        return False
        return True

    def action_info(self) -> bool:
        total = len(list(self.iter_pkgs()))
        new = len(list(self.iter_pkgs(IterPkgAction.NEW)))
        installed = total - new
        print(f"Packages: {total} | new: {new} | installed: {installed}")
        return True

    def iter_post_install_cmds(self, pkg: str):
        cmds = self.mynux.get("post_install_cmd", {}).get(pkg, [])
        if isinstance(cmds, list):
            yield from cmds
        if isinstance(cmds, str):
            yield cmds

    def iter_pkgs(self, pkg_action: IterPkgAction = IterPkgAction.ALL) -> Iterable:
        pkgs: List[str] = list(self.mynux.get("package", []))
        match pkg_action:
            case IterPkgAction.ALL:
                return iter(pkgs)
            case IterPkgAction.INSTALLED:
                return filter(check_pkg, pkgs)
            case IterPkgAction.NEW:
                return filter(lambda p: not check_pkg(p), pkgs)
            case _:
                raise Exception("WTF, how is this happening? Do you append the IterPkgAction?")
