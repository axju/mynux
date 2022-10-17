import subprocess  # nosec
from logging import getLogger
from pathlib import Path
from tempfile import mkdtemp

from .mynux import MynuxStorage
from .plain import Storage

logger = getLogger(__name__)


class RemoteGitStorageMixin(Storage):
    def __init__(self, path: Path, url: str | None = None):
        super().__init__(path)
        self.url = url or self.load_url()

    def __bool__(self):
        git_dir: Path = self.path / ".git"
        return super().__bool__() and git_dir.is_dir()

    def __eq__(self, other):
        return self.url == other.url

    def action_info(self) -> bool:
        super().action_info()
        print(f"Url:      {self.url}")
        return True

    def load_url(self):
        """
        get url from .git/config
        """
        git_conf: Path = self.path / ".git" / "config"
        if not git_conf.is_file():
            return ""

        with git_conf.open() as file:
            for line in file.readlines():
                url_index = line.find("url")
                if url_index >= 0:
                    return line[url_index + 6 :]
        return ""

    @classmethod
    def create_tmp(cls, url: str):
        path = Path(mkdtemp())
        subprocess.run(["git", "clone", url, path])  # nosec
        if MynuxStorage(path):
            return RemoteGitMynuxStorage(path, url)
        return cls(path, url)


class RemoteGitStorage(RemoteGitStorageMixin, Storage):
    ...


class RemoteGitMynuxStorage(RemoteGitStorageMixin, MynuxStorage):
    ...
