from pathlib import Path
from enum import Enum

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException, SQLParseException
from .patterns import (
    query_name_definition_pattern,
    empty_pattern,
    doc_comment_pattern,
    valid_query_name_pattern,
)


_ADAPTERS = {
    "aiosqlite": AioSQLiteAdapter,
    "asyncpg": AsyncPGAdapter,
    "psycopg2": PsycoPG2Adapter,
    "sqlite3": SQLite3DriverAdapter,
}


def register_driver_adapter(driver_name, driver_adapter):
    """Registers custom driver adapter classes to extend ``aiosql`` to to handle additional drivers.

    For details on how to create a new driver adapter see the documentation `link <https://nackjiholson.github.io/aiosql>`_.
    TODO: Make a link to the documentation when it exists.

    Args:
        driver_name (str): The driver type name.
        driver_adapter (callable): Either n class or function which creates an instance of a
                                   driver adapter.

    Returns:
        None

    Examples:
        To register a new loader::

            class MyDbAdapter():
                def process_sql(self, name, op_type, sql):
                    pass

                def select(self, conn, sql, parameters):
                    pass

                @contextmanager
                def select(self, conn, sql, parameters):
                    pass

                def insert_update_delete(self, conn, sql, parameters):
                    pass

                def insert_update_delete_many(self, conn, sql, parameters):
                    pass

                def insert_returning(self, conn, sql, parameters):
                    pass

                def execute_script(self, conn, sql):
                    pass


            aiosql.register_driver_adapter("mydb", MyDbAdapter)

        If your adapter constructor takes arguments you can register a function which can build
        your adapter instance::

            def adapter_factory():
                return MyDbAdapter("foo", 42)

            aiosql.register_driver_adapter("mydb", adapter_factory)

    """
    _ADAPTERS[driver_name] = driver_adapter


def get_driver_adapter(driver_name):
    """Get the driver adapter instance registered by the ``driver_name``.

    Args:
        driver_name (str): The database driver name.

    Returns:
        object: A driver adapter class.
    """
    try:
        driver_adapter = _ADAPTERS[driver_name]
    except KeyError:
        raise ValueError(f"Encountered unregistered driver_name: {driver_name}")

    return driver_adapter()


class SQLOperationType(Enum):
    """Enumeration of aiosql operation types.
    """

    INSERT_RETURNING = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    SCRIPT = 3
    SELECT = 4


class Queries:
    """Container object with dynamic methods built from SQL queries.

    The ``-- name`` definition comments in the SQL content determine what the dynamic
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

        for query_name, fn in queries:
            self.add_query(query_name, fn)

    @property
    def available_queries(self):
        """Returns listing of all the available query methods loaded in this class.

        Returns:
            list(str): List of dot-separated method accessor names.
        """
        return sorted(self._available_queries)

    def __repr__(self):
        return "Queries(" + self.available_queries.__repr__() + ")"

    def add_query(self, query_name, fn):
        """Adds a new dynamic method to this class.

        Args:
            query_name (str): The method name as found in the SQL content.
            fn (function): The loaded query function.

        Returns:

        """
        setattr(self, query_name, fn)
        self._available_queries.add(query_name)

    def add_child_queries(self, child_name, child_queries):
        """Adds a Queries object as a property.

        Args:
            child_name (str): The property name to group the child queries under.
            child_queries (Queries): Queries instance to add as sub-queries.

        Returns:
            None

        """
        setattr(self, child_name, child_queries)
        for child_name in child_queries.available_queries:
            self._available_queries.add(f"{child_name}.{child_name}")


def _create_fns(query_name, docs, op_type, sql, driver_adapter):
    def fn(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        if op_type == SQLOperationType.INSERT_RETURNING:
            return driver_adapter.insert_returning(conn, query_name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE:
            return driver_adapter.insert_update_delete(conn, query_name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
            return driver_adapter.insert_update_delete_many(conn, query_name, sql, *parameters)
        elif op_type == SQLOperationType.SCRIPT:
            return driver_adapter.execute_script(conn, sql)
        elif op_type == SQLOperationType.SELECT:
            return driver_adapter.select(conn, query_name, sql, parameters)
        else:
            raise ValueError(f"Unknown op_type: {op_type}")

    fn.__name__ = query_name
    fn.__docs__ = docs
    fn.sql = sql

    async def aio_fn(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        if op_type == SQLOperationType.INSERT_RETURNING:
            return await driver_adapter.insert_returning(conn, query_name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE:
            return await driver_adapter.insert_update_delete(conn, query_name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
            return await driver_adapter.insert_update_delete_many(
                conn, query_name, sql, *parameters
            )
        elif op_type == SQLOperationType.SCRIPT:
            return await driver_adapter.execute_script(conn, sql)
        elif op_type == SQLOperationType.SELECT:
            return await driver_adapter.select(conn, query_name, sql, parameters)
        else:
            raise ValueError(f"Unknown op_type: {op_type}")

    aio_fn.__name__ = query_name
    aio_fn.__docs__ = docs
    aio_fn.sql = sql

    ctx_mgr_method_name = f"{query_name}_cursor"

    def ctx_mgr(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        return driver_adapter.select_cursor(conn, query_name, sql, parameters)

    ctx_mgr.__name__ = ctx_mgr_method_name
    ctx_mgr.__docs__ = docs
    ctx_mgr.sql = sql

    if getattr(driver_adapter, "is_aio_driver", False):
        if op_type == SQLOperationType.SELECT:
            return [(query_name, aio_fn), (ctx_mgr_method_name, ctx_mgr)]
        else:
            return [(query_name, aio_fn)]
    else:
        if op_type == SQLOperationType.SELECT:
            return [(query_name, fn), (ctx_mgr_method_name, ctx_mgr)]
        else:
            return [(query_name, fn)]


def load_methods(sql_text, driver_adapter):
    lines = sql_text.strip().splitlines()
    query_name = lines[0].replace("-", "_")

    if query_name.endswith("<!"):
        op_type = SQLOperationType.INSERT_RETURNING
        query_name = query_name[:-2]
    elif query_name.endswith("*!"):
        op_type = SQLOperationType.INSERT_UPDATE_DELETE_MANY
        query_name = query_name[:-2]
    elif query_name.endswith("!"):
        op_type = SQLOperationType.INSERT_UPDATE_DELETE
        query_name = query_name[:-1]
    elif query_name.endswith("#"):
        op_type = SQLOperationType.SCRIPT
        query_name = query_name[:-1]
    else:
        op_type = SQLOperationType.SELECT

    if not valid_query_name_pattern.match(query_name):
        raise SQLParseException(f'name must convert to valid python variable, got "{query_name}".')

    docs = ""
    sql = ""
    for line in lines[1:]:
        match = doc_comment_pattern.match(line)
        if match:
            docs += match.group(1) + "\n"
        else:
            sql += line + "\n"

    docs = docs.strip()
    sql = driver_adapter.process_sql(query_name, op_type, sql.strip())

    return _create_fns(query_name, docs, op_type, sql, driver_adapter)


def load_queries_from_sql(sql, driver_adapter):
    queries = []
    for query_text in query_name_definition_pattern.split(sql):
        if not empty_pattern.match(query_text):
            for method_pair in load_methods(query_text, driver_adapter):
                queries.append(method_pair)
    return queries


def load_queries_from_file(file_path, driver_adapter):
    with file_path.open() as fp:
        return load_queries_from_sql(fp.read(), driver_adapter)


def load_queries_from_dir_path(dir_path, query_loader):
    if not dir_path.is_dir():
        raise ValueError(f"The path {dir_path} must be a directory")

    def _recurse_load_queries(path):
        queries = Queries()
        for p in path.iterdir():
            if p.is_file() and p.suffix != ".sql":
                continue
            elif p.is_file() and p.suffix == ".sql":
                for query_name, fn in load_queries_from_file(p, query_loader):
                    queries.add_query(query_name, fn)
            elif p.is_dir():
                child_name = p.relative_to(dir_path).name
                child_queries = _recurse_load_queries(p)
                queries.add_child_queries(child_name, child_queries)
            else:
                # This should be practically unreachable.
                raise SQLLoadException(f"The path must be a directory or file, got {p}")
        return queries

    return _recurse_load_queries(dir_path)


def from_str(sql, driver_name):
    """Load queries from a SQL string.

    Args:
        sql (str) A string containing SQL statements and aiosql name:
        driver_name (str): The database driver to use to load and execute queries.

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

            -- name: get-users-by-username
            -- Get all the users from the database,
            -- and return it as a dict
            select * from users where username =:username;
            \"""

            queries = aiosql.from_str(sql_text, db_driver="sqlite3")
            # Example usage after loading:
            # queries.get_all_greetings(conn)
            # queries.get_users_by_username(conn, username="willvaughn")

    """
    driver_adapter = get_driver_adapter(driver_name)
    return Queries(load_queries_from_sql(sql, driver_adapter))


def from_path(sql_path, driver_name):
    """Load queries from a sql file, or a directory of sql files.

    Args:
        sql_path (str|Path): Path to a ``.sql`` file or directory containing ``.sql`` files.
        driver_name (str): The database driver to use to load and execute queries.

    Returns:
        Queries

    Example:
        Loading queries paths::

            import sqlite3
            import aiosql

            queries = aiosql.from_path("./greetings.sql", driver_name="sqlite3")
            queries2 = aiosql.from_path("./sql_dir", driver_name="sqlite3")

    """
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    driver_adapter = get_driver_adapter(driver_name)

    if path.is_file():
        return Queries(load_queries_from_file(path, driver_adapter))
    elif path.is_dir():
        return load_queries_from_dir_path(path, driver_adapter)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
