import inspect
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    ContextManager,
    Dict,
    Generator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)
from typing import Protocol

# FIXME None added for MySQL buggy drivers
ParamType = Union[Dict[str, Any], List[Any], None]


class SQLOperationType(Enum):
    """Enumeration of aiosql operation types."""

    INSERT_RETURNING = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    SCRIPT = 3
    SELECT = 4
    SELECT_ONE = 5
    SELECT_VALUE = 6


class QueryDatum(NamedTuple):
    query_name: str
    doc_comments: str
    operation_type: SQLOperationType
    sql: str
    record_class: Any
    signature: Optional[inspect.Signature]
    floc: Tuple[Union[Path, str], int]
    attributes: Optional[Dict[str, Dict[str, str]]]
    parameters: Optional[List[str]]


class QueryFn(Protocol):
    __name__: str
    __signature__: Optional[inspect.Signature]
    sql: str
    operation: SQLOperationType
    attributes: Optional[Dict[str, Dict[str, str]]]
    parameters: Optional[List[str]]

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...  # pragma: no cover


# Can't make this a recursive type in terms of itself
# QueryDataTree = Dict[str, Union[QueryDatum, 'QueryDataTree']]
QueryDataTree = Dict[str, Union[QueryDatum, Dict]]


class SyncDriverAdapterProtocol(Protocol):
    def process_sql(
        self, query_name: str, op_type: SQLOperationType, sql: str
    ) -> str: ...  # pragma: no cover

    def select(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: ParamType,
        record_class: Optional[Callable],
    ) -> Generator[Any, None, None]: ...  # pragma: no cover

    def select_one(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: ParamType,
        record_class: Optional[Callable],
    ) -> Optional[Tuple[Any, ...]]: ...  # pragma: no cover

    def select_value(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> Optional[Any]: ...  # pragma: no cover

    def select_cursor(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> ContextManager[Any]: ...  # pragma: no cover

    def insert_update_delete(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> int: ...  # pragma: no cover

    def insert_update_delete_many(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> int: ...  # pragma: no cover

    def insert_returning(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> Optional[Any]: ...  # pragma: no cover

    def execute_script(self, conn: Any, sql: str) -> str: ...  # pragma: no cover


class AsyncDriverAdapterProtocol(Protocol):
    def process_sql(
        self, query_name: str, op_type: SQLOperationType, sql: str
    ) -> str: ...  # pragma: no cover

    async def select(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: ParamType,
        record_class: Optional[Callable],
    ) -> List: ...  # pragma: no cover

    async def select_one(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: ParamType,
        record_class: Optional[Callable],
    ) -> Optional[Any]: ...  # pragma: no cover

    async def select_value(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> Optional[Any]: ...  # pragma: no cover

    async def select_cursor(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> AsyncContextManager[Any]: ...  # pragma: no cover

    # TODO: Next major version introduce a return? Optional return?
    async def insert_update_delete(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> None: ...  # pragma: no cover

    # TODO: Next major version introduce a return? Optional return?
    async def insert_update_delete_many(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> None: ...  # pragma: no cover

    async def insert_returning(
        self, conn: Any, query_name: str, sql: str, parameters: ParamType
    ) -> Optional[Any]: ...  # pragma: no cover

    async def execute_script(self, conn: Any, sql: str) -> str: ...  # pragma: no cover


DriverAdapterProtocol = Union[SyncDriverAdapterProtocol, AsyncDriverAdapterProtocol]
