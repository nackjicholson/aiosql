# standard adapters
from .pyformat import PyFormatAdapter
from .generic import GenericAdapter
from .sqlite3 import SQLite3Adapter

# async adapters
from .aiosqlite import AioSQLiteAdapter
from .asyncpg import AsyncPGAdapter

# silence flake8 F401 warning:
_ALL = [
    PyFormatAdapter,
    GenericAdapter,
    SQLite3Adapter,
    AioSQLiteAdapter,
    AsyncPGAdapter,
]
