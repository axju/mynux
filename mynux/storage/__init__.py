from logging import getLogger
from pathlib import Path

from .mynux import MynuxStorage
from .plain import Storage

logger = getLogger(__name__)


def load(url: str | None) -> Storage | None:
    """
    load storage subclass from single string or return the system storage
    path=kind|content:
        "local|/path/to/dot/dir/or/mynux.toml"
        "git|git@github.com:username/repo.git"
        "git|https://github.com/username/project.git"
        "github|username/project"
    """
    if url is None:
        return None
    match url.split("|", 1):
        case ["local", content]:
            return load_local(Path(content))
        case ["git", content]:
            return load_git(content)
        case _:
            storage = load_local(Path(url))
            if isinstance(storage, Storage):
                return storage
    return None


def load_git(url: str):
    raise NotImplementedError


def load_local(path: Path):
    """
    try to load local storage from path
    (MynuxStorage, PlainStorage)
    """
    for cls in [MynuxStorage, Storage]:
        storage = cls(path)
        if storage:
            return storage
    return None
