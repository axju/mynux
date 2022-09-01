from typing import Optional

from logging import getLogger
from pathlib import Path

from ..utils import FileOperation, check_filter, file_operation_main, iter_gitignore_filter

logger = getLogger(__name__)


class Storage:
    """
    A simple dotfile directory, no extra mynux.toml file :(
    But good enough to list, copy or link the files.
    """

    DEFAULT_FILTER = [".git/*", "mynux.toml", "*README*"]

    DEFAULT_ACTIONS = {"info": False, "file": ["target_dir", "file_operation"]}

    def __init__(self, path: Path):
        self.path = path.resolve()
        if self.path.is_file() and self.path.parent.is_dir():
            self.path = self.path.parent
        self.filters = list(self.iter_filter())

    def __bool__(self):
        return self.path.is_dir()

    def __call__(self, name: str | None = None, **kwargs) -> bool:
        try:
            return self.action(name, **kwargs)
        except Exception as exc:
            logger.exception('Fail to call "%s".', self, exc_info=exc)
        return False

    def check_action(self, name: str) -> bool:
        return hasattr(self, f"action_{name}")

    def action(self, name: str | None = None, **kwargs) -> bool:
        """execute a single action or all DEFAULT_ACTIONS"""
        if name is None:
            for action, args in self.DEFAULT_ACTIONS.items():
                action_kwargs = {}
                match args:
                    case list():
                        action_kwargs = {arg: kwargs.get(arg) for arg in args if arg in kwargs}
                    case False:
                        continue
                # exit if any action fail
                if not self.action(action, **action_kwargs):
                    return False
            return True

        func = getattr(self, f"action_{name}", None)
        if func:
            return func(**kwargs)
        logger.warning('The action "%s" is not available in the class "%s"!', name, self.__class__)
        return False

    def action_file(self, target_dir=Path.home(), default_file_operation: FileOperation = FileOperation.LINK) -> bool:
        """
        copy, link or append files and even more in the mynux class
        """
        for source_file, target_file in self.iter_files(target_dir):
            file_operation_main(source_file, target_file, default_file_operation)
        return True

    def action_info(self) -> bool:
        for file in self.iter_files():
            print(file)
        return True

    def iter_files(self, target_dir: Optional[Path] = None):
        """
        iterate source files (and target files)
        """
        if target_dir is None:
            for file in self.path.glob("**/*"):
                if file.is_file() and not check_filter(file, self.filters):
                    yield file.resolve()
        else:
            target_dir = target_dir.resolve()
            for file in self.path.glob("**/*"):
                if file.is_file() and not check_filter(file, self.filters):
                    yield file.resolve(), target_dir / file.relative_to(self.path)

    def iter_filter(self):
        filters = []
        for name in self.DEFAULT_FILTER:
            filters.append(name)
            yield name

        yield ".gitignore"
        for name in iter_gitignore_filter(self.path / ".gitignore"):
            if name in filters:
                continue
            filters.append(name)
            yield name
