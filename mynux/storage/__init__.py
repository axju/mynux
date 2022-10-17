from typing import Sequence

import subprocess  # nosec
from logging import getLogger
from pathlib import Path
from tempfile import mkdtemp

from .mynux import MynuxStorage
from .plain import Storage
from .remote import RemoteGitMynuxStorage, RemoteGitStorage

logger = getLogger(__name__)

ALL_STORAGE_CLS: tuple[type[Storage], ...] = (RemoteGitMynuxStorage, RemoteGitStorage, MynuxStorage, Storage)


def load(url: str | None) -> Storage | None:
    """Load storage subclass from single string.
    Args:
        url (str | None): String to load. Like:
            "local|/path/to/dot/dir/or/mynux.toml"
            "git|git@github.com:username/repo.git"
            "git|https://github.com/username/project.git"
            "github|username/project"
    Returns:
        Storage | None: The Storage or None if storage can not load.
    """
    if url is None:
        return None
    match url.split("|", 1):
        case ["local", content]:
            return load_local(Path(content))
        case ["git", content]:
            return load_git(content)
        case _:
            if storage := load_local(Path(url)):
                return storage
            if storage := load_git(url):
                return storage
    return None


def load_storage(classes: tuple[type[Storage], ...] = ALL_STORAGE_CLS, **kwargs) -> Storage | None:
    """Get the widget under the given coordinates.
    Args:
        classes (tuple[type[Storage]): A tuple of Storage classes to check.
        **kwargs: arguments for the Storage class.
    Returns:
        Storage | None: The Storage or None if storage can not load.
    """
    for cls in classes:
        storage = cls(**kwargs)
        if storage:
            return storage
    return None


def load_local(path: Path) -> Storage | None:
    """
    try to load local storage from path
    (RemoteGitMynuxStorage, RemoteGitStorage, MynuxStorage, Storage)
    """
    return load_storage(path=path)


def load_git(url: str) -> Storage | None:
    """
    load git url to local tmp dir
    """
    path = Path(mkdtemp())
    subprocess.run(["git", "clone", url, path])  # nosec
    return load_storage(path=path, classes=(RemoteGitMynuxStorage, RemoteGitStorage))


def iter_storage_dir(path: Path):
    """
    iter through local storage directory
    """
    if path.is_dir():
        for storage_path in path.iterdir():
            if storage := load_local(storage_path):
                yield storage
