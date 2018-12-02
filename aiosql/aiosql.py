import re
from pathlib import Path

from .loaders.aiosqlite import AioSQLiteQueryLoader
from .loaders.asyncpg import AsyncPGQueryLoader
from .loaders.psycopg2 import PsycoPG2QueryLoader
from .loaders.sqlite3 import SQLite3QueryLoader
from .exceptions import SQLLoadException

namedef_pattern = re.compile(r"--\s*name\s*:\s*")
empty_pattern = re.compile(r"^\s*$")


_LOADERS = {
    "aiosqlite": lambda: AioSQLiteQueryLoader(),
    "asyncpg": lambda: AsyncPGQueryLoader(),
    "psycopg2": lambda: PsycoPG2QueryLoader(),
    "sqlite3": lambda: SQLite3QueryLoader(),
}


def register_query_loader(db_driver, loader):
    """Registers custom QueryLoader classes to extend ``aiosql`` to to handle new driver types.

    For details on how to create new ``QueryLoader`` see the
    :py:class:`aiosql.loaders.base.QueryLoader` documentation.

    Args:
        db_driver (str): The driver type name.
        loader: (aiosql.QueryLoader|function) Either an instance of a QueryLoader or
                                              a function which builds an instance.

    Returns:
        None

    Example:
        To register a new loader::

            import aiosql

            class MyDbLoader(aiosql.QueryLoader):
                # ... overrides process_sql and create_fn
                pass

            aiosql.register_query_loader('mydb', MyDbLoader())

    """
    _LOADERS[db_driver] = loader


def get_query_loader(db_driver):
    """Get the QueryLoader instance for registered by the ``db_driver`` name.

    Args:
        db_driver (str): The driver type name.

    Returns:
        aiosql.QueryLoader An instance of QueryLoader for the given db_driver.
    """
    try:
        loader = _LOADERS[db_driver]
    except KeyError:
        raise ValueError(f"Encountered unregistered db_driver: {db_driver}")

    return loader() if callable(loader) else loader


class Queries:
    """Container object containing methods built from SQL queries.

    The ``-- name: foobar`` definition comments in the SQL content determine what the dynamic
    methods of this class will be named.

    @DynamicAttrs
    """

    def __init__(self, queries=None):
        """Queries constructor.

        Args:
            queries (list(tuple)):
        """
        if queries is None:
            queries = []
        self._available_queries = set()

        for name, fn in queries:
            self.add_query(name, fn)

    @property
    def available_queries(self):
        """Returns listing of all the available query methods loaded in this class.

        Returns:
            list(str): List of dot-separated method accessor names.
        """
        return sorted(self._available_queries)

    def __repr__(self):
        return "Queries(" + self.available_queries.__repr__() + ")"

    def add_query(self, name, fn):
        """Adds a new dynamic method to this class.

        Args:
            name (str): The method name as found in the SQL content.
            fn (function): The loaded query function built by a QueryLoader class.

        Returns:

        """
        setattr(self, name, fn)
        self._available_queries.add(name)

    def add_child_queries(self, name, child_queries):
        """Adds a Queries object as a property.

        Args:
            name (str): The property name to group the child queries under.
            child_queries (Queries): Queries instance to add as sub-queries.

        Returns:
            None

        """
        setattr(self, name, child_queries)
        for child_name in child_queries.available_queries:
            self._available_queries.add(f"{name}.{child_name}")


def load_queries_from_sql(sql, query_loader):
    queries = []
    for query_text in namedef_pattern.split(sql):
        if not empty_pattern.match(query_text):
            queries.append(query_loader.load(query_text))
    return queries


def load_queries_from_file(file_path, query_loader):
    with file_path.open() as fp:
        return load_queries_from_sql(fp.read(), query_loader)


def load_queries_from_dir_path(dir_path, query_loader):
    if not dir_path.is_dir():
        raise ValueError(f"The path {dir_path} must be a directory")

    def _recurse_load_queries(path):
        queries = Queries()
        for p in path.iterdir():
            if p.is_file() and p.suffix != ".sql":
                continue
            elif p.is_file() and p.suffix == ".sql":
                for name, fn in load_queries_from_file(p, query_loader):
                    queries.add_query(name, fn)
            elif p.is_dir():
                child_name = p.relative_to(dir_path).name
                child_queries = _recurse_load_queries(p)
                queries.add_child_queries(child_name, child_queries)
            else:
                raise RuntimeError(p)
        return queries

    return _recurse_load_queries(dir_path)


def from_str(sql, db_driver):
    """Load queries from a SQL string.

    Args:
        sql (str) A string containing SQL statements and aiosql name:
        db_driver (str): The database driver to use to load and execute queries.

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

            -- name: $get-users-by-username
            -- Get all the users from the database,
            -- and return it as a dict
            select * from users where username =:username;
            \"""

            queries = aiosql.from_str(sql_text, db_driver="sqlite3")
            # Example usage after loading:
            # queries.get_all_greetings(conn)
            # queries.get_users_by_username(conn, username="willvaughn")

    """
    query_loader = get_query_loader(db_driver)
    return Queries(load_queries_from_sql(sql, query_loader))


def from_path(sql_path, db_driver):
    """Load queries from a sql file, or a directory of sql files.

    Args:
        sql_path (str|Path): Path to a ``.sql`` file or directory containing ``.sql`` files.
        db_driver (str): The database driver to use to load and execute queries.

    Returns:
        Queries

    Example:
        Loading queries paths::

            import sqlite3
            import aiosql

            queries = aiosql.from_path("./greetings.sql", db_driver="sqlite3")
            queries2 = aiosql.from_path("./sql_dir", db_driver="sqlite3")

    """
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    query_loader = get_query_loader(db_driver)

    if path.is_file():
        return Queries(load_queries_from_file(path, query_loader))
    elif path.is_dir():
        return load_queries_from_dir_path(path, query_loader)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
