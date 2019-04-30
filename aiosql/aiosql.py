from pathlib import Path
from enum import Enum
from types import MethodType
from typing import List, NamedTuple, Dict, Union, Callable, Tuple, Any, Optional

from .adapters.aiosqlite import AioSQLiteAdapter
from .adapters.asyncpg import AsyncPGAdapter
from .adapters.psycopg2 import PsycoPG2Adapter
from .adapters.sqlite3 import SQLite3DriverAdapter
from .exceptions import SQLLoadException, SQLParseException
from .patterns import (
    query_name_definition_pattern,
    query_row_class_definition_pattern,
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


def make_driver_adapter(driver_adapter: Union[str, Any]):
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
    row_class: Any = None


def _create_methods(query_datum: QueryDatum, is_aio=True) -> List[Tuple[str, Callable]]:
    query_name, doc_comments, operation_type, sql, row_class = query_datum
    # sql = driver_adapter.process_sql(query_name, operation_type, sql)

    if is_aio:

        async def fn(self, conn, *args, **kwargs):
            parameters = kwargs if len(kwargs) > 0 else args
            if operation_type == SQLOperationType.INSERT_RETURNING:
                return await self.driver_adapter.insert_returning(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE:
                return await self.driver_adapter.insert_update_delete(
                    conn, query_name, sql, parameters
                )
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
                return await self.driver_adapter.insert_update_delete_many(
                    conn, query_name, sql, *parameters
                )
            elif operation_type == SQLOperationType.SCRIPT:
                return await self.driver_adapter.execute_script(conn, sql)
            elif operation_type == SQLOperationType.SELECT:
                return await self.driver_adapter.select(conn, query_name, sql, parameters)
            else:
                raise ValueError(f"Unknown op_type: {operation_type}")

    else:

        def fn(self, conn, *args, **kwargs):
            parameters = kwargs if len(kwargs) > 0 else args
            if operation_type == SQLOperationType.INSERT_RETURNING:
                return self.driver_adapter.insert_returning(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE:
                return self.driver_adapter.insert_update_delete(conn, query_name, sql, parameters)
            elif operation_type == SQLOperationType.INSERT_UPDATE_DELETE_MANY:
                return self.driver_adapter.insert_update_delete_many(
                    conn, query_name, sql, *parameters
                )
            elif operation_type == SQLOperationType.SCRIPT:
                return self.driver_adapter.execute_script(conn, sql)
            elif operation_type == SQLOperationType.SELECT:
                return self.driver_adapter.select(conn, query_name, sql, parameters, row_class)
            else:
                raise ValueError(f"Unknown op_type: {operation_type}")

    fn.__name__ = query_name
    fn.__doc__ = doc_comments
    fn.sql = sql

    ctx_mgr_method_name = f"{query_name}_cursor"

    def ctx_mgr(self, conn, *args, **kwargs):
        parameters = kwargs if len(kwargs) > 0 else args
        return self.driver_adapter.select_cursor(conn, query_name, sql, parameters)

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


class QueryParser:
    def __init__(self, driver_adapter, row_classes: Optional[Dict]):
        self.driver_adapter = driver_adapter
        self.row_classes = row_classes if row_classes is not None else {}

    def _make_query_datum(self, query_str: str):
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

        row_class_match = query_row_class_definition_pattern.match(lines[1])
        if row_class_match:
            line_offset = 2
            row_class_name = row_class_match.group(1)
        else:
            line_offset = 1
            row_class_name = None

        doc_comments = ""
        sql = ""
        for line in lines[line_offset:]:
            doc_match = doc_comment_pattern.match(line)
            if doc_match:
                doc_comments += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        doc_comments = doc_comments.strip()
        sql = self.driver_adapter.process_sql(query_name, operation_type, sql)
        row_class = self.row_classes.get(row_class_name)

        return QueryDatum(query_name, doc_comments, operation_type, sql, row_class)

    def load_query_data_from_sql(self, sql: str) -> List[QueryDatum]:
        query_data = []
        for query_sql_str in query_name_definition_pattern.split(sql):
            if not empty_pattern.match(query_sql_str):
                query_data.append(self._make_query_datum(query_sql_str))
        return query_data

    def load_query_data_from_file(self, file_path: Path) -> List[QueryDatum]:
        with file_path.open() as fp:
            return self.load_query_data_from_sql(fp.read())

    def load_query_data_from_dir_path(self, dir_path) -> QueryDataTree:
        if not dir_path.is_dir():
            raise ValueError(f"The path {dir_path} must be a directory")

        def _recurse_load_query_data_tree(path):
            # queries = Queries()
            query_data_tree = {}
            for p in path.iterdir():
                if p.is_file() and p.suffix != ".sql":
                    continue
                elif p.is_file() and p.suffix == ".sql":
                    for query_datum in self.load_query_data_from_file(p):
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

    def __init__(self, driver_adapter):
        """Queries constructor.

        Args:
            driver_adapter (object):
        """
        self.driver_adapter = driver_adapter
        self.is_aio = getattr(driver_adapter, "is_aio_driver", False)
        self._available_queries = set()

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
            self.add_query(query_name, MethodType(fn, self))

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

    def load_from_list(self, query_data: List[QueryDatum], driver_adapter):
        for query_datum in query_data:
            self.add_queries(_create_methods(query_datum, driver_adapter))
        return self

    def load_from_tree(self, query_data_tree: QueryDataTree):
        for key, value in query_data_tree.items():
            if isinstance(value, dict):
                self.add_child_queries(key, Queries(self.driver_adapter).load_from_tree(value))
            else:
                self.add_queries(_create_methods(value, self.is_aio))
        return self


def from_str(sql, driver_adapter, row_classes=None):
    """Load queries from a SQL string.

    Args:
        sql (str) A string containing SQL statements and aiosql name:
        driver_adapter (str|Any): The database driver to use to load and execute queries.
        row_classes (dict|None):

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
    driver_adapter = make_driver_adapter(driver_adapter)
    query_parser = QueryParser(driver_adapter, row_classes)
    query_data = query_parser.load_query_data_from_sql(sql)
    return Queries(driver_adapter).load_from_list(query_data)


def from_path(
    sql_path: Union[str, Path], driver_adapter: Union[str, Any], row_classes: Optional[Dict] = None
):
    """Load queries from a sql file, or a directory of sql files.

    Args:
        sql_path (str|Path): Path to a ``.sql`` file or directory containing ``.sql`` files.
        driver_adapter (str|Any): The database driver to use to load and execute queries.
        row_classes (dict|None):

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

    driver_adapter = make_driver_adapter(driver_adapter)
    query_parser = QueryParser(driver_adapter, row_classes)

    if path.is_file():
        query_data = query_parser.load_query_data_from_file(path)
        return Queries(driver_adapter).load_from_list(query_data)
    elif path.is_dir():
        query_data_tree = query_parser.load_query_data_from_dir_path(path)
        return Queries(driver_adapter).load_from_tree(query_data_tree)
    else:
        raise SQLLoadException(f"The sql_path must be a directory or file, got {sql_path}")
