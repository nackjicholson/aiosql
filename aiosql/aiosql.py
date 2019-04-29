from pathlib import Path
from enum import Enum
from types import MethodType
from typing import List, NamedTuple, Dict, Union, Callable, Tuple

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException, SQLParseException
from .patterns import (
    query_name_definition_pattern,
    query_dataclass_definition_pattern,
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

    For details on how to create a new driver adapter see the documentation
    `link <https://nackjiholson.github.io/aiosql>`_.

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
                def select_cursor(self, conn, sql, parameters):
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


def get_driver_adapter(driver_name, dataclass_map):
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

    return driver_adapter(dataclass_map)


class SQLOperationType(Enum):
    """Enumeration of aiosql operation types.
    """

    INSERT_RETURNING = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    SCRIPT = 3
    SELECT = 4


class QueryDatum(NamedTuple):
    query_name: str
    doc_comments: str
    operation_type: SQLOperationType
    sql: str
    dataclass_name: str = None

    @staticmethod
    def from_sql_str(query_str: str):
        lines = query_str.strip().splitlines()
        query_name = lines[0].replace("-", "_")

        if query_name.endswith("<!"):
            operation_type = SQLOperationType.INSERT_RETURNING
            query_name = query_name[:-2]
        elif query_name.endswith("*!"):
            operation_type = SQLOperationType.INSERT_UPDATE_DELETE_MANY
            query_name = query_name[:-2]
        elif query_name.endswith("!"):
            operation_type = SQLOperationType.INSERT_UPDATE_DELETE
            query_name = query_name[:-1]
        elif query_name.endswith("#"):
            operation_type = SQLOperationType.SCRIPT
            query_name = query_name[:-1]
        else:
            operation_type = SQLOperationType.SELECT

        if not valid_query_name_pattern.match(query_name):
            raise SQLParseException(
                f'name must convert to valid python variable, got "{query_name}".'
            )

        # check if line 1 is dataset, if it is make a dataset name, else it's None?
        dataclass_match = query_dataclass_definition_pattern.match(lines[1])
        if dataclass_match:
            line_offset = 2
            dataclass_name = dataclass_match.group(1)
        else:
            line_offset = 1
            dataclass_name = None

        doc_comments = ""
        sql = ""
        for line in lines[line_offset:]:
            doc_match = doc_comment_pattern.match(line)
            if doc_match:
                doc_comments += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        doc_comments = doc_comments.strip()
        return QueryDatum(query_name, doc_comments, operation_type, sql, dataclass_name)


def _create_methods(query_datum: QueryDatum, driver_adapter) -> List[Tuple[str, Callable]]:
    is_aio_driver = getattr(driver_adapter, "is_aio_driver", False)
    query_name, doc_comments, operation_type, sql, _ = query_datum
    sql = driver_adapter.process_sql(query_name, operation_type, sql)

    if is_aio_driver:

        async def fn(conn, *args, **kwargs):
            parameters = kwargs if len(kwargs) > 0 else args
            if operation_type == SQLOperationType.INSERT_RETURNING:
                return await driver_adapter.insert_returning(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE:
                return await driver_adapter.insert_update_delete(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
                return await driver_adapter.insert_update_delete_many(
                    conn, query_name, sql, *parameters
                )
            elif operation_type == SQLOperationType.SCRIPT:
                return await driver_adapter.execute_script(conn, sql)
            elif operation_type == SQLOperationType.SELECT:
                return await driver_adapter.select(conn, query_name, sql, parameters)
            else:
                raise ValueError(f"Unknown op_type: {operation_type}")

    else:

        def fn(conn, *args, **kwargs):
            parameters = kwargs if len(kwargs) > 0 else args
            if operation_type == SQLOperationType.INSERT_RETURNING:
                return driver_adapter.insert_returning(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE:
                return driver_adapter.insert_update_delete(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
                return driver_adapter.insert_update_delete_many(conn, query_name, sql, *parameters)
            elif operation_type == SQLOperationType.SCRIPT:
                return driver_adapter.execute_script(conn, sql)
            elif operation_type == SQLOperationType.SELECT:
                return driver_adapter.select(conn, query_name, sql, parameters)
            else:
                raise ValueError(f"Unknown op_type: {operation_type}")

    fn.__name__ = query_name
    fn.__doc__ = doc_comments
    fn.sql = sql

    ctx_mgr_method_name = f"{query_name}_cursor"

    def ctx_mgr(conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        return driver_adapter.select_cursor(conn, query_name, sql, parameters)

    ctx_mgr.__name__ = ctx_mgr_method_name
    ctx_mgr.__doc__ = doc_comments
    ctx_mgr.sql = sql

    if operation_type == SQLOperationType.SELECT:
        return [(query_name, fn), (ctx_mgr_method_name, ctx_mgr)]
    else:
        return [(query_name, fn)]


def load_query_data_from_sql(sql: str) -> List[QueryDatum]:
    query_data = []
    for query_sql_str in query_name_definition_pattern.split(sql):
        if not empty_pattern.match(query_sql_str):
            query_data.append(QueryDatum.from_sql_str(query_sql_str))
    return query_data


def load_query_data_from_file(file_path: Path) -> List[QueryDatum]:
    with file_path.open() as fp:
        return load_query_data_from_sql(fp.read())


QueryDataTree = Dict[str, Union[QueryDatum, "QueryDataTree"]]


def load_query_data_from_dir_path(dir_path) -> QueryDataTree:
    if not dir_path.is_dir():
        raise ValueError(f"The path {dir_path} must be a directory")

    def _recurse_load_query_data_tree(path):
        # queries = Queries()
        query_data_tree = {}
        for p in path.iterdir():
            if p.is_file() and p.suffix != ".sql":
                continue
            elif p.is_file() and p.suffix == ".sql":
                for query_datum in load_query_data_from_file(p):
                    query_data_tree[query_datum.query_name] = query_datum
            elif p.is_dir():
                child_name = p.relative_to(dir_path).name
                child_query_data_tree = _recurse_load_query_data_tree(p)
                query_data_tree[child_name] = child_query_data_tree
            else:
                # This should be practically unreachable.
                raise SQLLoadException(f"The path must be a directory or file, got {p}")
        return query_data_tree

    return _recurse_load_query_data_tree(dir_path)


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
        self.add_queries(queries)

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

    def add_queries(self, queries):
        for query_name, fn in queries:
            self.add_query(query_name, fn)

    def add_child_queries(self, child_name, child_queries):
        """Adds a Queries object as a property.

        Args:
            child_name (str): The property name to group the child queries under.
            child_queries (Queries): Queries instance to add as sub-queries.

        Returns:
            None

        """
        setattr(self, child_name, child_queries)
        for child_query_name in child_queries.available_queries:
            self._available_queries.add(f"{child_name}.{child_query_name}")

    @staticmethod
    def from_list(query_data: List[QueryDatum], driver_adapter):
        queries = Queries()

        for query_datum in query_data:
            queries.add_queries(_create_methods(query_datum, driver_adapter))

        return queries

    @staticmethod
    def from_tree(query_data_tree: QueryDataTree, driver_adapter):
        queries = Queries()

        for key, value in query_data_tree.items():
            if isinstance(value, dict):
                queries.add_child_queries(key, Queries.from_tree(value, driver_adapter))
            else:
                queries.add_queries(_create_methods(value, driver_adapter))

        return queries


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
            queries.get_all_greetings(conn)
            queries.get_users_by_username(conn, username="willvaughn")

    """
    driver_adapter = get_driver_adapter(driver_name)
    query_data = load_query_data_from_sql(sql)
    return Queries.from_list(query_data, driver_adapter)


def from_path(sql_path, driver_name, dataclass_map=None):
    """Load queries from a sql file, or a directory of sql files.

    Args:
        sql_path (str|Path): Path to a ``.sql`` file or directory containing ``.sql`` files.
        driver_name (str): The database driver to use to load and execute queries.
        dataclass_map (dict|None):

    Returns:
        Queries: Queries object.

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

    driver_adapter = get_driver_adapter(driver_name, dataclass_map)

    if path.is_file():
        query_data = load_query_data_from_file(path)
        return Queries.from_list(query_data, driver_adapter)
    elif path.is_dir():
        query_data_tree = load_query_data_from_dir_path(path)
        return Queries.from_tree(query_data_tree, driver_adapter)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
