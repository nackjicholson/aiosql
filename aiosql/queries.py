from types import MethodType
from typing import Callable, List, Tuple

from .types import QueryDatum, QueryDataTree, SQLOperationType


def _create_methods(query_datum: QueryDatum, is_aio=True) -> List[Tuple[str, Callable]]:
    query_name, doc_comments, operation_type, sql, record_class = query_datum

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
                return await self.driver_adapter.select(
                    conn, query_name, sql, parameters, record_class
                )
            elif operation_type == SQLOperationType.SELECT_ONE:
                return await self.driver_adapter.select_one(
                    conn, query_name, sql, parameters, record_class
                )
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
                return self.driver_adapter.select(conn, query_name, sql, parameters, record_class)
            elif operation_type == SQLOperationType.SELECT_ONE:
                return self.driver_adapter.select_one(
                    conn, query_name, sql, parameters, record_class
                )
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

    def load_from_list(self, query_data: List[QueryDatum]):
        for query_datum in query_data:
            self.add_queries(_create_methods(query_datum, self.is_aio))
        return self

    def load_from_tree(self, query_data_tree: QueryDataTree):
        for key, value in query_data_tree.items():
            if isinstance(value, dict):
                self.add_child_queries(key, Queries(self.driver_adapter).load_from_tree(value))
            else:
                self.add_queries(_create_methods(value, self.is_aio))
        return self
