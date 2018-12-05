from pathlib import Path
from enum import Enum

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException, SQLParseException
from .patterns import namedef_pattern, empty_pattern, doc_pattern, name_pattern


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

    Example:
        To register a new loader::

            class MyDbAdapter():
                def process_sql(self, name, op_type, sql):
                    pass

                def select(self, conn, sql, parameters, return_as_dict):
                    pass

                def insert_update_delete(self, conn, sql, parameters):
                    pass

                def insert_update_delete_many(self, conn, sql, parameters):
                    pass

                def insert_returning(self, conn, sql, parameters):
                    pass

                def execute_script(self, conn, sql):
                    pass


            aiosql.register_driver_adapter('mydb', MyDbAdapter)

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

    SELECT = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    INSERT_RETURNING = 3
    SCRIPT = 4


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


def _create_fn(name, op_type, sql, return_as_dict, driver_adapter):
    def fn(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        if op_type == SQLOperationType.SELECT:
            return driver_adapter.select(conn, name, sql, parameters, return_as_dict)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE:
            return driver_adapter.insert_update_delete(conn, name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
            return driver_adapter.insert_update_delete_many(conn, name, sql, *parameters)
        elif op_type == SQLOperationType.INSERT_RETURNING:
            return driver_adapter.insert_returning(conn, name, sql, parameters)
        elif op_type == SQLOperationType.SCRIPT:
            return driver_adapter.execute_script(conn, sql)
        else:
            raise RuntimeError()

    return fn


def _create_aio_fn(name, op_type, sql, return_as_dict, driver_adapter):
    async def fn(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        if op_type == SQLOperationType.SELECT:
            return await driver_adapter.select(conn, name, sql, parameters, return_as_dict)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE:
            return await driver_adapter.insert_update_delete(conn, name, sql, parameters)
        elif op_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
            return await driver_adapter.insert_update_delete_many(conn, name, sql, *parameters)
        elif op_type == SQLOperationType.INSERT_RETURNING:
            return await driver_adapter.insert_returning(conn, name, sql, parameters)
        elif op_type == SQLOperationType.SCRIPT:
            return await driver_adapter.execute_script(conn, sql)
        else:
            raise RuntimeError()

    return fn


def load(sql_text, driver_adapter):
    lines = sql_text.strip().splitlines()
    name = lines[0].replace("-", "_")

    if name.endswith("<!"):
        op_type = SQLOperationType.INSERT_RETURNING
        name = name[:-2]
    elif name.endswith("*!"):
        op_type = SQLOperationType.INSERT_UPDATE_DELETE_MANY
        name = name[:-2]
    elif name.endswith("!"):
        op_type = SQLOperationType.INSERT_UPDATE_DELETE
        name = name[:-1]
    elif name.endswith("#"):
        op_type = SQLOperationType.SCRIPT
        name = name[:-1]
    else:
        op_type = SQLOperationType.SELECT

    return_as_dict = False
    if name.startswith("$"):
        return_as_dict = True
        name = name[1:]

    if not name_pattern.match(name):
        raise SQLParseException(f'name must convert to valid python variable, got "{name}".')

    docs = ""
    sql = ""
    for line in lines[1:]:
        match = doc_pattern.match(line)
        if match:
            docs += match.group(1) + "\n"
        else:
            sql += line + "\n"

    docs = docs.strip()
    sql = driver_adapter.process_sql(name, op_type, sql.strip())

    if driver_adapter.is_aio_driver:
        fn = _create_aio_fn(name, op_type, sql, return_as_dict, driver_adapter)
    else:
        fn = _create_fn(name, op_type, sql, return_as_dict, driver_adapter)

    fn.__name__ = name
    fn.__docs__ = docs
    fn.sql = sql
    return name, fn


def load_queries_from_sql(sql, driver_adapter):
    queries = []
    for query_text in namedef_pattern.split(sql):
        if not empty_pattern.match(query_text):
            queries.append(load(query_text, driver_adapter))
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
