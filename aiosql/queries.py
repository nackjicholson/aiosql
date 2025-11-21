import re
import inspect
from pathlib import Path
from types import MethodType

# TODO drop most of this ugly stuff when >= 3.10
from typing import Any, Callable, cast

from .types import DriverAdapterProtocol, QueryDatum, QueryDataTree, QueryFn, SQLOperationType
from .utils import SQLLoadException, SQLParseException, log


class Queries:
    """Container object with dynamic methods built from SQL queries.

    The ``-- name:`` definition comments in the content of the SQL determine what the dynamic
    methods of this class will be named.

    Much of the needed pre-processing is performed in ``QueryLoader``.

    Parameters:

    - :param driver_adapter: Either a string to designate one of the aiosql built-in database driver
      adapters (e.g. "sqlite3", "psycopg").
      If you have defined your own adapter class, you can pass its constructor.
    - :param kwargs_only: whether to reject positional parameters, defaults to true.
    """

    def __init__(
            self,
            driver_adapter: DriverAdapterProtocol,
            kwargs_only: bool = True,
        ):
        self.driver_adapter: DriverAdapterProtocol = driver_adapter
        self.is_aio: bool = getattr(driver_adapter, "is_aio_driver", False)
        self._kwargs_only = kwargs_only
        self._available_queries: set[str] = set()

    #
    # INTERNAL UTILS
    #
    def _params(
            self,
            attributes: dict[str, dict[str, str]]|None,
            params: list[str]|None,
            args: list[Any]|tuple[Any],
            kwargs: dict[str, Any],
        ) -> list[Any]|tuple[Any]|dict[str, Any]:
        """Handle query parameters.

        - update attribute references ``:u.a`` to ``:u__a``.
        - check whether non kwargs are allowed and other checks.
        - return the parameters, either ``args`` or ``kwargs``.
        """

        if attributes and kwargs:

            # switch o.a to o<attribute>a
            for var, atts in attributes.items():
                if var not in kwargs:
                    raise ValueError(f"missing named parameter {var}")
                val = kwargs.pop(var)
                for att, var_name in atts.items():
                    if not hasattr(val, att):
                        raise ValueError(f"parameter {var} is missing attribute {att}")
                    kwargs[var_name] = getattr(val, att)

        if self._kwargs_only:
            if args:
                raise ValueError("cannot use positional parameters under kwargs_only, use named parameters (name=value, …)")
            return kwargs
        elif kwargs:
            if args:
                raise ValueError("cannot mix positional and named parameters in query")
            return kwargs
        else:  # args
            if args and params is not None:
                raise ValueError("cannot use positional parameters with declared named parameters")
            return args

    def _look_like_a_select(self, sql: str) -> bool:
        """Tell whether sql may return a relation."""
        # skipped: VALUES, SHOW, TABLE, EXECUTE
        return re.search(r"(?i)\b(SELECT|RETURNING)\b", sql) is not None

    def _query_fn(
            self,
            fn: Callable[..., Any],
            name: str,
            doc: str|None,
            sql: str,
            operation: SQLOperationType,
            signature: inspect.Signature|None,
            floc: tuple[Path|str, int] = ("<unknown>", 0),
            attributes: dict[str, dict[str, str]]|None = None,
            params: list[str]|None = None,
        ) -> QueryFn:
        """Add custom-made metadata to a dynamically generated function."""
        fname, lineno = floc
        fn.__code__ = fn.__code__.replace(co_filename=str(fname), co_firstlineno=lineno)  # type: ignore
        qfn = cast(QueryFn, fn)
        qfn.__name__ = name
        qfn.__doc__ = doc
        qfn.__signature__ = signature
        # query details
        qfn.sql = sql
        qfn.operation = operation
        qfn.attributes = attributes
        qfn.parameters = params
        return qfn

    # NOTE about coverage: because __code__ is set to reflect the actual SQL file
    # source, coverage does note detect that the "fn" functions are actually called,
    # hence the "no cover" hints.
    def _make_sync_fn(self, query_datum: QueryDatum) -> QueryFn:
        """Build a synchronous dynamic method from a parsed query."""

        query_name, doc_comments, operation, sql, record_class, signature, floc, attributes, params = (
            query_datum
        )

        if operation == SQLOperationType.INSERT_RETURNING:

            def fn(self, conn, *args, **kwargs):  # pragma: no cover
                return self.driver_adapter.insert_returning(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        elif operation == SQLOperationType.INSERT_UPDATE_DELETE:

            def fn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                return self.driver_adapter.insert_update_delete(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        elif operation == SQLOperationType.INSERT_UPDATE_DELETE_MANY:

            def fn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                assert not kwargs, "cannot use named parameters in many query"  # help type checker
                return self.driver_adapter.insert_update_delete_many(conn, query_name, sql, *args)

        elif operation == SQLOperationType.SCRIPT:

            if params:  # pragma: no cover
                # NOTE this is caught earlier
                raise SQLParseException(f"cannot use named parameters in SQL script: {query_name}")

            def fn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                assert not args and not kwargs, f"cannot use parameters in SQL script: {query_name}"
                return self.driver_adapter.execute_script(conn, sql)

        elif operation == SQLOperationType.SELECT:

            # sanity check in passing…
            if not self._look_like_a_select(sql):
                fname, lineno = floc
                log.warning(f"query {query_name} at {fname}:{lineno} may not be a select, consider adding an operator, eg '!'")

            def fn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                return self.driver_adapter.select(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
                )

        elif operation == SQLOperationType.SELECT_ONE:

            def fn(self, conn, *args, **kwargs):  # pragma: no cover
                return self.driver_adapter.select_one(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
                )

        elif operation == SQLOperationType.SELECT_VALUE:

            def fn(self, conn, *args, **kwargs):  # pragma: no cover
                return self.driver_adapter.select_value(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        else:
            raise ValueError(f"Unknown operation: {operation}")

        return self._query_fn(
            fn, query_name, doc_comments, sql, operation, signature, floc, attributes, params
        )

    def _make_async_fn(self, query_datum: QueryDatum) -> QueryFn:
        """Build an asynchronous dynamic method from a parsed query."""

        query_name, doc_comments, operation, sql, record_class, signature, floc, attributes, params = (
            query_datum
        )

        if operation == SQLOperationType.INSERT_RETURNING:

            async def afn(self, conn, *args, **kwargs):  # pragma: no cover
                return await self.driver_adapter.insert_returning(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        elif operation == SQLOperationType.INSERT_UPDATE_DELETE:

            async def afn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                return await self.driver_adapter.insert_update_delete(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        elif operation == SQLOperationType.INSERT_UPDATE_DELETE_MANY:

            async def afn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                assert not kwargs, "cannot use named parameters in many query"  # help type checker
                return await self.driver_adapter.insert_update_delete_many(conn, query_name, sql, *args)

        elif operation == SQLOperationType.SCRIPT:

            if params:  # pragma: no cover
                # NOTE this is caught earlier
                raise SQLParseException(f"cannot use named parameters in SQL script: {query_name}")

            async def afn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                assert not args and not kwargs, f"cannot use parameters in SQL script: {query_name}"
                return await self.driver_adapter.execute_script(conn, sql)

        elif operation == SQLOperationType.SELECT:

            # sanity check in passing…
            if not self._look_like_a_select(sql):
                fname, lineno = floc
                log.warning(f"query {query_name} at {fname}:{lineno} may not be a select, consider adding an operator, eg '!'")

            # async generator
            async def afn(self, conn, *args, **kwargs):  # type: ignore # pragma: no cover
                async for row in self.driver_adapter.select(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
                ):
                    yield row

        elif operation == SQLOperationType.SELECT_ONE:

            async def afn(self, conn, *args, **kwargs):  # pragma: no cover
                return await self.driver_adapter.select_one(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs), record_class
                )

        elif operation == SQLOperationType.SELECT_VALUE:

            async def afn(self, conn, *args, **kwargs):  # pragma: no cover
                return await self.driver_adapter.select_value(
                    conn, query_name, sql, self._params(attributes, params, args, kwargs)
                )

        else:
            raise ValueError(f"Unknown operation: {operation}")  # pragma: no cover

        return self._query_fn(
            afn, query_name, doc_comments, sql, operation, signature, floc, attributes, params
        )

    def _make_ctx_mgr(self, fn: QueryFn) -> QueryFn:
        """Wrap in a context manager function."""

        def ctx_mgr(self, conn, *args, **kwargs):  # pragma: no cover
            return self.driver_adapter.select_cursor(
                conn, fn.__name__, fn.sql, self._params(fn.attributes, fn.parameters, args, kwargs)
            )

        return self._query_fn(
            ctx_mgr, f"{fn.__name__}_cursor", fn.__doc__, fn.sql, fn.operation, fn.__signature__
        )

    def _create_methods(self, query_datum: QueryDatum, is_aio: bool) -> list[QueryFn]:
        """Internal function to feed add_queries."""

        fn = self._make_async_fn(query_datum) if is_aio else self._make_sync_fn(query_datum)

        # context manager
        if query_datum.operation_type == SQLOperationType.SELECT:
            ctx_mgr = self._make_ctx_mgr(fn)
            return [fn, ctx_mgr]
        else:
            return [fn]

    #
    # PUBLIC INTERFACE
    #
    @property
    def available_queries(self) -> list[str]:
        """Returns listing of all the available query methods loaded in this class.

        **Returns:** ``list[str]`` List of dot-separated method accessor names.
        """
        return sorted(self._available_queries)

    def __repr__(self) -> str:
        return "Queries(" + self.available_queries.__repr__() + ")"

    def add_query(self, query_name: str, fn: Callable) -> None:
        """Adds a new dynamic method to this class.

        **Parameters:**

        - **query_name** - The method name as found in the SQL content.
        - **fn** - The loaded query function.
        """
        if hasattr(self, query_name):
            # this is filtered out because it can lead to hard to find bugs.
            raise SQLLoadException(f"cannot override existing attribute with query: {query_name}")
        setattr(self, query_name, fn)
        self._available_queries.add(query_name)

    def add_queries(self, queries: list[QueryFn]) -> None:
        """Add query methods to `Queries` instance."""
        for fn in queries:
            query_name = fn.__name__.rpartition(".")[2]
            self.add_query(query_name, MethodType(fn, self))

    def add_child_queries(self, child_name: str, child_queries: "Queries") -> None:
        """Adds a Queries object as a property.

        **Parameters:**

        - **child_name** - The property name to group the child queries under.
        - **child_queries** - Queries instance to add as sub-queries.
        """
        if hasattr(self, child_name):  # pragma: no cover
            # this is filtered out because it can lead to hard to find bugs.
            raise SQLLoadException(f"cannot override existing attribute with child: {child_name}")
        setattr(self, child_name, child_queries)
        for child_query_name in child_queries.available_queries:
            self._available_queries.add(f"{child_name}.{child_query_name}")

    def load_from_list(self, query_data: list[QueryDatum]):
        """Load Queries from a list of `QueryDatum`"""
        for query_datum in query_data:
            self.add_queries(self._create_methods(query_datum, self.is_aio))
        return self

    def load_from_tree(self, query_data_tree: QueryDataTree):
        """Load Queries from a `QueryDataTree`"""
        for key, value in query_data_tree.items():
            if isinstance(value, dict):
                self.add_child_queries(key, Queries(self.driver_adapter, self._kwargs_only).load_from_tree(value))
            else:
                self.add_queries(self._create_methods(value, self.is_aio))
        return self
