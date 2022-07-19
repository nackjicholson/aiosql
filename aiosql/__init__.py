from .aiosql import from_path, from_str, register_adapter
from .exceptions import SQLParseException, SQLLoadException

import pkg_resources as pkg  # type: ignore

__version__ = pkg.require("aiosql")[0].version

__all__ = ["from_path", "from_str", "register_adapter", "SQLParseException", "SQLLoadException"]
