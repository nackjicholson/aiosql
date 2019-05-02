from pathlib import Path
from typing import Dict, Union, Any, Optional

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException

from .queries import Queries
from .query_loader import QueryLoader


_ADAPTERS = {
    "aiosqlite": AioSQLiteAdapter,
    "asyncpg": AsyncPGAdapter,
    "psycopg2": PsycoPG2Adapter,
    "sqlite3": SQLite3DriverAdapter,
}


def _make_driver_adapter(driver_adapter: Union[str, Any]):
    """Get the driver adapter instance registered by the ``driver_name``.

    Args:
        driver_adapter (str|Any): The database driver name.

    Returns:
        object: A driver adapter class.
    """
    if isinstance(driver_adapter, str):
        try:
            driver_adapter = _ADAPTERS[driver_adapter]
        except KeyError:
            raise ValueError(f"Encountered unregistered driver_adapter: {driver_adapter}")

    return driver_adapter()


def from_str(sql, driver_adapter, record_classes=None):
    """Load queries from a SQL string.

    Args:
        sql (str) A string containing SQL statements and aiosql name:
        driver_adapter (str|Any): Either a string to designate one of the aiosql built-in
                                  database driver adapters. One of "sqlite3", "psycopg2",
                                  "aiosqlite", or "asyncpg". If you have defined your own adapter
                                  class, you can pass it's constructor.
        record_classes (dict|None): Mapping of strings used in "record_class" declarations to the
                                    python classes which aiosql should use when marshaling SQL
                                    results.

    Returns:
        Queries

    Example:
        Loading queries from a SQL string::

            import sqlite3
            import aiosql

            sql_text = \"""
            -- name: get-all-greetings
            -- Get all the greetings in the database
            select * from greetings;

            -- name: get-user-by-username^
            -- Get all the users from the database,
            -- and return it as a dict
            select * from users where username =:username;
            \"""

            queries = aiosql.from_str(sql_text, "sqlite3")
            queries.get_all_greetings(conn)
            queries.get_user_by_username(conn, username="willvaughn")

    """
    driver_adapter = _make_driver_adapter(driver_adapter)
    query_loader = QueryLoader(driver_adapter, record_classes)
    query_data = query_loader.load_query_data_from_sql(sql)
    return Queries(driver_adapter).load_from_list(query_data)


def from_path(
    sql_path: Union[str, Path],
    driver_adapter: Union[str, Any],
    record_classes: Optional[Dict] = None,
):
    """Load queries from a ``.sql`` file, or directory of ``.sql`` files.

    Args:
        sql_path (str|Path): Path to a ``.sql`` file or directory containing ``.sql`` files.
        driver_adapter (str|Any): Either a string to designate one of the aiosql built-in
                                  database driver adapters. One of "sqlite3", "psycopg2",
                                  "aiosqlite", or "asyncpg". If you have defined your own adapter
                                  class, you can pass it's constructor.
        record_classes (dict|None): Mapping of strings used in "record_class" declarations to the
                                    python classes which aiosql should use when marshaling SQL
                                    results.

    Returns:
        Queries: Queries object.

    Example::

        >>> aiosql.from_path("./sql", "pscycopg2")
        >>> aiosql.from_path("./sql", MyDBAdapter)
        >>> aiosql.from_path("./sql/users.sql", "aiosqlite", record_classes={"User": User})

    """
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    driver_adapter = _make_driver_adapter(driver_adapter)
    query_loader = QueryLoader(driver_adapter, record_classes)

    if path.is_file():
        query_data = query_loader.load_query_data_from_file(path)
        return Queries(driver_adapter).load_from_list(query_data)
    elif path.is_dir():
        query_data_tree = query_loader.load_query_data_from_dir_path(path)
        return Queries(driver_adapter).load_from_tree(query_data_tree)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
