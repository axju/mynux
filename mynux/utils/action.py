from typing import Dict, List

from logging import getLogger

logger = getLogger(__name__)


class ActionCls:
    """
    just handel the action calls
    """

    DEFAULT_ACTIONS: Dict[str, List | bool] = {}

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
