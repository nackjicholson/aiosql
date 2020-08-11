from pathlib import Path
from typing import Callable, Dict, Optional, Type, Union

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException
from .queries import Queries
from .query_loader import QueryLoader
from .types import DriverAdapterProtocol


_ADAPTERS: Dict[str, Callable[..., DriverAdapterProtocol]] = {
    "aiosqlite": AioSQLiteAdapter,
    "asyncpg": AsyncPGAdapter,
    "psycopg2": PsycoPG2Adapter,
    "sqlite3": SQLite3DriverAdapter,
}


def _make_driver_adapter(
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]]
) -> DriverAdapterProtocol:
    """Get the driver adapter instance registered by the `driver_name`.
    """
    if isinstance(driver_adapter, str):
        try:
            driver_adapter = _ADAPTERS[driver_adapter]
        except KeyError:
            raise ValueError(f"Encountered unregistered driver_adapter: {driver_adapter}")

    return driver_adapter()


def from_str(
    sql: str,
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    *,
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
):
    """Load queries from a SQL string.

    **Parameters:**

    * **sql** - A string containing SQL statements and aiosql name.
    * **driver_adapter** - Either a string to designate one of the aiosql built-in database driver
    adapters. One of "sqlite3", "psycopg2", "aiosqlite", or "asyncpg". If you have defined your
    own adapter class, you can pass it's constructor.
    * **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
    declarations to the python classes which aiosql should use when marshaling SQL results.
    * **loader_cls** - *(optional)* Custom constructor for QueryLoader extensions.
    * **queries_cls** - *(optional)* Custom constructor for Queries extensions.

    **Returns:** `Queries`

    Usage:

    Loading queries from a SQL string.

    ```python
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
    ```
    """
    adapter = _make_driver_adapter(driver_adapter)
    query_loader = loader_cls(adapter, record_classes)
    query_data = query_loader.load_query_data_from_sql(sql)
    return queries_cls(adapter).load_from_list(query_data)


def from_path(
    sql_path: Union[str, Path],
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    *,
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
):
    """Load queries from a `.sql` file, or directory of `.sql` files.

    **Parameters:**

    * **sql_path** - Path to a `.sql` file or directory containing `.sql` files.
    * **driver_adapter** - Either a string to designate one of the aiosql built-in database driver
    adapters. One of "sqlite3", "psycopg2", "aiosqlite", or "asyncpg". If you have defined your own
    adapter class, you may pass its constructor.
    * **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
    declarations to the python classes which aiosql should use when marshaling SQL results.
    * **loader_cls** - *(optional)* Custom constructor for `QueryLoader` extensions.
    * **queries_cls** - *(optional)* Custom constructor for `Queries` extensions.

    **Returns:** `Queries`

    Usage:

    ```python
    >>> queries = aiosql.from_path("./sql", "pscycopg2")
    >>> queries = aiosql.from_path("./sql", MyDBAdapter)
    ```
    """
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    adapter = _make_driver_adapter(driver_adapter)
    query_loader = loader_cls(adapter, record_classes)

    if path.is_file():
        query_data = query_loader.load_query_data_from_file(path)
        return queries_cls(adapter).load_from_list(query_data)
    elif path.is_dir():
        query_data_tree = query_loader.load_query_data_from_dir_path(path)
        return queries_cls(adapter).load_from_tree(query_data_tree)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
