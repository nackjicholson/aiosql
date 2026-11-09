from .aiosql import from_path, from_str, register_adapter
from .utils import SQLParseException, SQLLoadException
from importlib.metadata import version

__version__ = version("aiosql")

# exported package interface
__all__ = [
    "SQLLoadException",
    "SQLParseException",
    "from_path",
    "from_str",
    "register_adapter"
]
