from .aiosql import from_path, from_str, register_adapter
from .utils import SQLParseException, SQLLoadException

# TODO python >= 3.8
#   from importlib.metadata import version
#   __version__ = version("aiosql")
import pkg_resources as pkg  # type: ignore

__version__ = pkg.require("aiosql")[0].version

__all__ = ["from_path", "from_str", "register_adapter", "SQLParseException", "SQLLoadException"]
