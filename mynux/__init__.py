from typing import Dict

import sys

from mynux.utils.__init__ import iter_cmds

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


__version__: str = get_version()

cmds = dict(iter_cmds())

config: Dict[str, Dict] = {}
