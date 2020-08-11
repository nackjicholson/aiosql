from enum import Enum
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    ContextManager,
    Dict,
    List,
    NamedTuple,
    Optional,
    Union,
)

from typing_extensions import Protocol


class SQLOperationType(Enum):
    """Enumeration of aiosql operation types.
    """

    INSERT_RETURNING = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    SCRIPT = 3
    SELECT = 4
    SELECT_ONE = 5


class QueryDatum(NamedTuple):
    query_name: str
    doc_comments: str
    operation_type: SQLOperationType
    sql: str
    record_class: Any = None


# Can't make this a recursive type in terms of itself
# QueryDataTree = Dict[str, Union[QueryDatum, 'QueryDataTree']]
QueryDataTree = Dict[str, Union[QueryDatum, Dict]]


class SyncDriverAdapterProtocol(Protocol):
    def process_sql(self, query_name: str, op_type: SQLOperationType, sql: str) -> str:
        ...

    def select(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: Union[List, Dict],
        record_class=Optional[Callable],
    ) -> List:
        ...

    def select_one(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: Union[List, Dict],
        record_class=Optional[Callable],
    ) -> Optional[Any]:
        ...

    def select_cursor(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> ContextManager[Any]:
        ...

    # TODO: Next major version introduce a return? Optional return?
    def insert_update_delete(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> None:
        ...

    # TODO: Next major version introduce a return? Optional return?
    def insert_update_delete_many(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> None:
        ...

    def insert_returning(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> Optional[Any]:
        ...

    # TODO: Next major version introduce a return? Optional return?
    def execute_script(self, conn: Any, sql: str) -> None:
        ...


class AsyncDriverAdapterProtocol(Protocol):
    def process_sql(self, query_name: str, op_type: SQLOperationType, sql: str) -> str:
        ...

    async def select(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: Union[List, Dict],
        record_class=Optional[Callable],
    ) -> List:
        ...

    async def select_one(
        self,
        conn: Any,
        query_name: str,
        sql: str,
        parameters: Union[List, Dict],
        record_class=Optional[Callable],
    ) -> Optional[Any]:
        ...

    async def select_cursor(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> AsyncContextManager[Any]:
        ...

    # TODO: Next major version introduce a return? Optional return?
    async def insert_update_delete(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> None:
        ...

    # TODO: Next major version introduce a return? Optional return?
    async def insert_update_delete_many(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> None:
        ...

    async def insert_returning(
        self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
    ) -> Optional[Any]:
        ...

    # TODO: Next major version introduce a return? Optional return?
    async def execute_script(self, conn: Any, sql: str) -> None:
        ...


DriverAdapterProtocol = Union[SyncDriverAdapterProtocol, AsyncDriverAdapterProtocol]
