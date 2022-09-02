from typing import Dict

import fnmatch
import re
import shutil
import subprocess  # nosec
import sys
from argparse import ArgumentParser
from enum import Enum
from importlib.metadata import entry_points
from logging import getLogger
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib  # pylint: disable=import-error
else:
    import tomli as tomllib

logger = getLogger(__name__)


class FileOperation(Enum):
    LINK = 1
    COPY = 2
    APPEND = 3

    @classmethod
    def get_from_str(cls, name: str, default=None):
        match name.lower():
            case "link" | "ln":
                return cls.LINK
            case "copy" | "cp":
                return cls.COPY
            case "append" | "add" | "+":
                return cls.APPEND
        return default


class UserAction(Enum):
    ASK = 1
    DELETE = 2
    SKIPP = 3


def get_mynux_arg_parser(prog: str) -> ArgumentParser:
    return ArgumentParser(prog=f"mynux {prog}")


def ask_to_confirm(msg: str, default: bool = True) -> bool:
    """ask user boolean question"""
    if default:
        result = input(msg + "[Y/n] ") or "y"
    else:
        result = input(msg + "[y/N] ") or "n"
    return result.lower() in ["y", "yes"]


def iter_cmds():
    for entry_point in entry_points().select(group="mynux.cmd"):
        yield entry_point.name, entry_point


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
        for name in gitignore_filters:
            if not name or name.startswith("#"):
                continue
            yield name


def check_target_file(target_file: Path, user_action: UserAction = UserAction.ASK) -> bool:
    """
    Check if the target file exist. Return only True if file did not exist.
    If the target file exist it could be deleted:
    UserAction.ASK -> the user can decide
              .DELETE -> deleting file
              .SKIPP -> return False, file would be there
    """
    if not target_file.is_file() and not target_file.is_symlink():
        return True

    match user_action:
        case UserAction.ASK:
            if (input(f'File "{target_file}" exist! Overwrite? [Y/n] ') or "Y") in ["y", "Y", "yes"]:
                target_file.unlink()
            else:
                logger.info('skipp file "%s" by user', target_file)
                return False
        case UserAction.DELETE:
            target_file.unlink()
        case UserAction.SKIPP:
            return False
        case _:
            raise Exception("WTF, how is this happening? Do you append the UserAction?")

    # just to make sure that the file is deleted
    return not target_file.is_file() and not target_file.is_symlink()


def file_operation_link(source_file: Path, target_file: Path, user_action: UserAction = UserAction.ASK) -> bool:
    if not check_target_file(target_file, user_action):
        return False
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.symlink_to(source_file)
        return True
    except Exception as exc:
        logger.error("Error at file_operation_link", exc_info=exc)
        return False


def file_operation_copy(source_file: Path, target_file: Path, user_action: UserAction = UserAction.ASK) -> bool:
    if not check_target_file(target_file, user_action):
        return False
    try:
        target_file.unlink(missing_ok=True)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source_file, target_file)
        return True
    except Exception as exc:
        logger.error("Error at file_operation_copy", exc_info=exc)
        return False


def file_operation_append(source_file: Path, target_file: Path) -> bool:
    raise NotImplementedError


def file_operation_main(source_file: Path, target_file: Path, file_operation: FileOperation) -> bool:
    match file_operation:
        case FileOperation.LINK:
            result = file_operation_link(source_file, target_file)
        case FileOperation.COPY:
            result = file_operation_copy(source_file, target_file)
        case FileOperation.APPEND:
            result = file_operation_append(source_file, target_file)
        case _:
            result = False
    if result:
        logger.info('Install file "%s" to "%s".', source_file, target_file)
    else:
        logger.warning('Fail to install file "%s" to "%s".', source_file, target_file)
    return result


def check_pkg(pkg: str) -> bool:
    """return True if package is installed"""
    proc = subprocess.run(["pacman", "-Qn", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # nosec
    if proc.returncode == 0:
        return True

    proc = subprocess.run(["pacman", "-Qg", pkg], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)  # nosec
    group_pkg = [line.decode().split()[1] for line in proc.stdout.splitlines()]
    return proc.returncode == 0 and all(map(check_pkg, group_pkg))


def load_toml(path: Path) -> Dict:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except Exception as exc:
        logger.exception('Fail to load "%s".', path, exc_info=exc)
    return {}
