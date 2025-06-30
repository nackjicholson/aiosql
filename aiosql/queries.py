import re
import inspect
from pathlib import Path
from types import MethodType
from typing import Any, Callable, List, Optional, Set, Tuple, Union, Dict, cast

from .types import DriverAdapterProtocol, QueryDatum, QueryDataTree, QueryFn, SQLOperationType
from .utils import SQLLoadException, SQLParseException, log

class Queries:
    """
    Container for dynamic methods built from SQL queries.
    SQL definition comments (e.g., `-- name:`) determine dynamic method names.
    Most pre-processing is performed in `QueryLoader`.
    """

    def __init__(
        self,
        driver_adapter: DriverAdapterProtocol,
        kwargs_only: bool = True,
    ) -> None:
        self.driver_adapter: DriverAdapterProtocol = driver_adapter
        self.is_aio: bool = getattr(driver_adapter, "is_aio_driver", False)
        self._kwargs_only = kwargs_only
        self._available_queries: Set[str] = set()

    # --- Internal Utilities ---

    def _params(
        self,
        attributes: Optional[Dict[str, Dict[str, str]]],
        params: Optional[List[str]],
        args: Union[List[Any], Tuple[Any]],
        kwargs: Dict[str, Any],
    ) -> Union[List[Any], Tuple[Any], Dict[str, Any]]:
        """
        Handle query parameters:
        - Update attribute references `:u.a` to `:u__a`.
        - Check whether non-kwargs are allowed.
        - Return the parameters (args or kwargs).
        """
        if attributes and kwargs:
            for var, atts in attributes.items():
                if var not in kwargs:
                    raise ValueError(f"Missing named parameter: '{var}'")
                val = kwargs.pop(var)
                for att, var_name in atts.items():
                    if not hasattr(val, att):
                        raise ValueError(f"Parameter '{var}' is missing attribute '{att}'")
                    kwargs[var_name] = getattr(val, att)

        if self._kwargs_only:
            if args:
                raise ValueError(
                    "Positional parameters are not allowed with 'kwargs_only'; use named parameters (name=value, ...)."
                )
            return kwargs
        if kwargs:
            if args:
                raise ValueError(
                    "Cannot mix positional and named parameters in query."
                )
            return kwargs
        if args and params is not None:
            raise ValueError(
                "Cannot use positional parameters with declared named parameters."
            )
        return args

    @staticmethod
    def _looks_like_select(sql: str) -> bool:
        """Return True if sql appears to return a relation (SELECT/RETURNING)."""
        return re.search(r"(?i)\b(SELECT|RETURNING)\b", sql) is not None

    def _query_fn(
        self,
        fn: Callable[..., Any],
        name: str,
        doc: Optional[str],
        sql: str,
        operation: SQLOperationType,
        signature: Optional[inspect.Signature],
        floc: Tuple[Union[Path, str], int] = ("<unknown>", 0),
        attributes: Optional[Dict[str, Dict[str, str]]] = None,
        params: Optional[List[str]] = None,
    ) -> QueryFn:
        """
        Attach custom metadata to a dynamically generated function.
        """
        fname, lineno = floc
        fn.__code__ = fn.__code__.replace(co_filename=str(fname), co_firstlineno=lineno)  # type: ignore
        qfn = cast(QueryFn, fn)
        qfn.__name__ = name
        qfn.__doc__ = doc
        qfn.__signature__ = signature
        qfn.sql = sql
        qfn.operation = operation
        qfn.attributes = attributes
        qfn.parameters = params
        return qfn

    def _make_sync_fn(self, query_datum: QueryDatum) -> QueryFn:
        """
        Build a dynamic method from a parsed query (synchronous version).
        """
        (
            query_name, doc_comments, operation, sql, record_class, signature,
            floc, attributes, params
        ) = query_datum

        # Map operation type to method
        def _raise_sql_parse_exception():
            raise SQLParseException(f"Cannot use named parameters in SQL script: {query_name}")

        fn_map = {
            SQLOperationType.INSERT_RETURNING: lambda self, conn, *args, **kwargs: self.driver_adapter.insert_returning(
                conn, query_name, sql, self._params(attributes, params, args, kwargs)
            ),
            SQLOperationType.INSERT_UPDATE_DELETE: lambda self, conn, *args, **kwargs: self.driver_adapter.insert_update_delete(
                conn, query_name, sql, self._params(attributes, params, args, kwargs)
            ),
            SQLOperationType.INSERT_UPDATE_DELETE_MANY: lambda self, conn, *args, **kwargs: (
                (lambda: (_ for _ in ()).throw(AssertionError("Cannot use named parameters in many query")))
                if kwargs else self.driver_adapter.insert_update_delete_many(conn, query_name, sql, *args)
            ),
            SQLOperationType.SCRIPT: lambda self, conn, *args, **kwargs: (
                (lambda: (_ for _ in ()).throw(SQLParseException(f"Cannot use named parameters in SQL script: {query_name}")))
                if params else (
                    (lambda: (_ for _ in ()).throw(AssertionError(f"Cannot use parameters in SQL script: {query_name}")))
                    if args or kwargs else self.driver_adapter.execute_script(conn, sql)
                )
            ),
            SQLOperationType.SELECT: lambda self, conn, *args, **kwargs: self.driver_adapter.select(
                conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
            ),
            SQLOperationType.SELECT_ONE: lambda self, conn, *args, **kwargs: self.driver_adapter.select_one(
                conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
            ),
            SQLOperationType.SELECT_VALUE: lambda self, conn, *args, **kwargs: self.driver_adapter.select_value(
                conn, query_name, sql, self._params(attributes, params, args, kwargs)
            ),
        }

        if operation == SQLOperationType.SELECT and not self._looks_like_select(sql):
            fname, lineno = floc
            log.warning(
                f"Query '{query_name}' at {fname}:{lineno} may not be a select; consider adding an operator, e.g., '!'."
            )

        if operation not in fn_map:
            raise ValueError(f"Unknown operation: {operation}")

        fn = fn_map[operation]

        def dynamic_fn(self, conn, *args, **kwargs):
            return fn(self, conn, *args, **kwargs)

        return self._query_fn(
            dynamic_fn, query_name, doc_comments, sql, operation, signature, floc, attributes, params
        )

    def _make_async_fn(self, fn: QueryFn) -> QueryFn:
        """Wrap a sync function as async."""
        async def afn(self, conn, *args, **kwargs):
            return await fn(self, conn, *args, **kwargs)
        return self._query_fn(
            afn, fn.__name__, fn.__doc__, fn.sql, fn.operation, fn.__signature__
        )

    def _make_ctx_mgr(self, fn: QueryFn) -> QueryFn:
        """Wrap a function in a context manager."""
        def ctx_mgr(self, conn, *args, **kwargs):
            return self.driver_adapter.select_cursor(
                conn, fn.__name__, fn.sql, self._params(fn.attributes, fn.parameters, args, kwargs)
            )
        return self._query_fn(
            ctx_mgr, f"{fn.__name__}_cursor", fn.__doc__, fn.sql, fn.operation, fn.__signature__
        )

    def _create_methods(self, query_datum: QueryDatum, is_aio: bool) -> List[QueryFn]:
        """Return method(s) for a given query datum."""
        fn = self._make_sync_fn(query_datum)
        if is_aio:
            fn = self._make_async_fn(fn)
        if query_datum.operation_type == SQLOperationType.SELECT:
            return [fn, self._make_ctx_mgr(fn)]
        return [fn]

    # --- Public Interface ---

    @property
    def available_queries(self) -> List[str]:
        """List of all loaded query method names."""
        return sorted(self._available_queries)

    def __repr__(self) -> str:
        return f"Queries({self.available_queries!r})"

    def add_query(self, query_name: str, fn: Callable) -> None:
        """Add a dynamic method to this class."""
        if hasattr(self, query_name):
            raise SQLLoadException(f"Cannot override existing attribute with query: '{query_name}'")
        setattr(self, query_name, fn)
        self._available_queries.add(query_name)

    def add_queries(self, queries: List[QueryFn]) -> None:
        """Add query methods to this Queries instance."""
        for fn in queries:
            query_name = fn.__name__.rpartition(".")[2]
            self.add_query(query_name, MethodType(fn, self))

    def add_child_queries(self, child_name: str, child_queries: "Queries") -> None:
        """Add a Queries object as a property (sub-queries)."""
        if hasattr(self, child_name):
            raise SQLLoadException(f"Cannot override existing attribute with child: '{child_name}'")
        setattr(self, child_name, child_queries)
        for child_query_name in child_queries.available_queries:
            self._available_queries.add(f"{child_name}.{child_query_name}")

    def load_from_list(self, query_data: List[QueryDatum]) -> "Queries":
        """Load Queries from a list of QueryDatum."""
        for query_datum in query_data:
            self.add_queries(self._create_methods(query_datum, self.is_aio))
        return self

    def load_from_tree(self, query_data_tree: QueryDataTree) -> "Queries":
        """Load Queries from a QueryDataTree."""
        for key, value in query_data_tree.items():
            if isinstance(value, dict):
                child = Queries(self.driver_adapter, self._kwargs_only).load_from_tree(value)
                self.add_child_queries(key, child)
            else:
                self.add_queries(self._create_methods(value, self.is_aio))
        return self
