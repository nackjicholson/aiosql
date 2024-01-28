from pathlib import Path
from typing import Callable, Dict, Optional, Type, Union, Tuple

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.pyformat import PyFormatAdapter
from .adapters.mysql import BrokenMySQLAdapter
from .adapters.generic import GenericAdapter
from .adapters.sqlite3 import SQLite3Adapter
from .adapters.pg8000 import Pg8000Adapter
from .adapters.duckdb import DuckDBAdapter
from .utils import SQLLoadException, log
from .queries import Queries
from .query_loader import QueryLoader
from .types import DriverAdapterProtocol

_ADAPTERS: Dict[str, Callable[..., DriverAdapterProtocol]] = {
    "aiosqlite": AioSQLiteAdapter,  # type: ignore
    "apsw": GenericAdapter,
    "asyncpg": AsyncPGAdapter,  # type: ignore
    "mariadb": BrokenMySQLAdapter,
    "mysqldb": BrokenMySQLAdapter,
    "mysql-connector": PyFormatAdapter,
    "pg8000": Pg8000Adapter,
    "psycopg": PyFormatAdapter,
    "psycopg2": PyFormatAdapter,
    "pygresql": PyFormatAdapter,
    "pymysql": BrokenMySQLAdapter,
    "sqlite3": SQLite3Adapter,
    "duckdb": DuckDBAdapter,
}


def register_adapter(name: str, adapter: Callable[..., DriverAdapterProtocol]):
    """Register or override an adapter."""
    if name.lower() in _ADAPTERS:
        log.warning(f"overriding aiosql adapter {name}")
    _ADAPTERS[name.lower()] = adapter


def _make_driver_adapter(
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]]
) -> DriverAdapterProtocol:
    """Get the driver adapter instance registered by the `driver_name`."""
    if isinstance(driver_adapter, str):
        try:
            driver_adapter = _ADAPTERS[driver_adapter.lower()]
        except KeyError:
            raise ValueError(f"Encountered unregistered driver_adapter: {driver_adapter}")
    # try some guessing if it is a PEP249 module
    elif hasattr(driver_adapter, "paramstyle"):
        style = getattr(driver_adapter, "paramstyle")  # avoid mypy warning?
        if style == "pyformat":
            driver_adapter = PyFormatAdapter  # type: ignore
        elif style == "named":
            driver_adapter = GenericAdapter  # type: ignore
        else:
            raise ValueError(f"Unexpected driver_adapter: {driver_adapter} ({style})")
    # so, can we just call it?
    if not callable(driver_adapter):
        raise ValueError(f"Unexpected driver_adapter: {driver_adapter}")

    return driver_adapter()


def from_str(
    sql: str,
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    kwargs_only: bool = False,
    *,
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
):
    """Load queries from a SQL string.

    **Parameters:**

    - **sql** - A string containing SQL statements and aiosql name.
    - **driver_adapter** - Either a string to designate one of the aiosql built-in database driver
      adapters. One of many available for SQLite, Postgres and MySQL. If you have defined your
      own adapter class, you can pass it's constructor.
    - **kwargs_only** - Whether to only use named parameters on query execution.
    - **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
      declarations to the python classes which aiosql should use when marshaling SQL results.
    - **loader_cls** - *(optional)* Custom constructor for QueryLoader extensions.
    - **queries_cls** - *(optional)* Custom constructor for Queries extensions.

    **Returns:** ``Queries``

    Usage:

    Loading queries from a SQL string.

    .. code-block:: python

      import sqlite3
      import aiosql

      sql_text = \"""
      -- name: get-all-greetings
      -- Get all the greetings in the database
      select * from greetings;

      -- name: get-user-by-username^
      -- Get all the users from the database,
      -- and return it as a dict
      select * from users where username = :username;
      \"""

      queries = aiosql.from_str(sql_text, "sqlite3")
      queries.get_all_greetings(conn)
      queries.get_user_by_username(conn, username="willvaughn")

    """
    adapter = _make_driver_adapter(driver_adapter)
    query_loader = loader_cls(adapter, record_classes)
    query_data = query_loader.load_query_data_from_sql(sql, [])
    return queries_cls(adapter, kwargs_only=kwargs_only).load_from_list(query_data)


def from_path(
    sql_path: Union[str, Path],
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    kwargs_only: bool = False,
    *,
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
    ext: Tuple[str] = (".sql",),
    encoding=None,
):
    """Load queries from a `.sql` file, or directory of `.sql` files.

    **Parameters:**

    - **sql_path** - Path to a `.sql` file or directory containing `.sql` files.
    - **driver_adapter** - Either a string to designate one of the aiosql built-in database driver
      adapters. One of many available for SQLite, Postgres and MySQL. If you have defined your own
      adapter class, you may pass its constructor.
    - **kwargs_only** - Whether to only use named parameters on query execution.
    - **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
      declarations to the python classes which aiosql should use when marshaling SQL results.
    - **loader_cls** - *(optional)* Custom constructor for `QueryLoader` extensions.
    - **queries_cls** - *(optional)* Custom constructor for `Queries` extensions.
    - **ext** - *(optional)* allowed file extensions for query files, default is `(".sql",)`.
    - **encoding** - *(optional)* encoding for reading files.

    **Returns:** `Queries`

    Usage:

    .. code-block:: python

      queries = aiosql.from_path("./sql", "psycopg2")
      queries = aiosql.from_path("./sql", MyDBAdapter)
    """
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    adapter = _make_driver_adapter(driver_adapter)
    query_loader = loader_cls(adapter, record_classes)

    if path.is_file():
        query_data = query_loader.load_query_data_from_file(path, encoding=encoding)
        return queries_cls(adapter, kwargs_only=kwargs_only).load_from_list(query_data)
    elif path.is_dir():
        query_data_tree = query_loader.load_query_data_from_dir_path(
            path, ext=ext, encoding=encoding
        )
        return queries_cls(adapter, kwargs_only=kwargs_only).load_from_tree(query_data_tree)
    else:  # pragma: no cover
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
