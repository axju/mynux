from typing import Optional

import subprocess  # nosec
from logging import getLogger
from pathlib import Path

from .plain import Storage

logger = getLogger(__name__)


class RemoteGitStorage(Storage):
    def __init__(self, path: Path, url: Optional[str]):
        super().__init__(path)
        self.url = url or ""  # TODO: load url from .git

    def clone(self, path: Path):
        subprocess.run(["git", "clone", self.url, path])  # nosec
        return RemoteGitStorage(path, self.url)
