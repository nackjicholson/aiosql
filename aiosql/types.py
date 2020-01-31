from enum import Enum
from pathlib import Path
from typing import Dict, Union, NamedTuple, Any


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
    file_path: Path
    record_class: Any = None


QueryDataTree = Dict[str, Union[QueryDatum, "QueryDataTree"]]
