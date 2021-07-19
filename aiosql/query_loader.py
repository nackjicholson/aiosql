from pathlib import Path
from typing import Dict, List, Optional

from .exceptions import SQLParseException, SQLLoadException
from .patterns import (
    doc_comment_pattern,
    empty_pattern,
    query_record_class_definition_pattern,
    query_name_definition_pattern,
    valid_query_name_pattern,
)
from .types import QueryDatum, QueryDataTree, SQLOperationType, DriverAdapterProtocol


class QueryLoader:
    def __init__(self, driver_adapter: DriverAdapterProtocol, record_classes: Optional[Dict]):
        self.driver_adapter = driver_adapter
        self.record_classes = record_classes if record_classes is not None else {}

    def _make_query_datum(self, query_str: str, ns_parts: List):
        lines = [line.strip() for line in query_str.strip().splitlines()]
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
        elif query_name.endswith("^"):
            operation_type = SQLOperationType.SELECT_ONE
            query_name = query_name[:-1]
        elif query_name.endswith("$"):
            operation_type = SQLOperationType.SELECT_VALUE
            query_name = query_name[:-1]
        else:
            operation_type = SQLOperationType.SELECT

        if not valid_query_name_pattern.match(query_name):
            raise SQLParseException(
                f'name must convert to valid python variable, got "{query_name}".'
            )

        record_class_match = query_record_class_definition_pattern.match(lines[1])
        record_class_name: Optional[str]
        if record_class_match:
            line_offset = 2
            record_class_name = record_class_match.group(1)
        else:
            line_offset = 1
            record_class_name = None

        doc_comments = ""
        sql = ""
        for line in lines[line_offset:]:
            doc_match = doc_comment_pattern.match(line)
            if doc_match:
                doc_comments += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        query_fqn = ".".join(ns_parts + [query_name])
        doc_comments = doc_comments.strip()
        sql = self.driver_adapter.process_sql(query_fqn, operation_type, sql.strip())
        # TODO: Probably will want this to be a class, marshal in, and marshal out
        record_class = self.record_classes.get(record_class_name)

        return QueryDatum(query_fqn, doc_comments, operation_type, sql, record_class)

    def load_query_data_from_sql(
        self, sql: str, ns_parts: Optional[List] = None
    ) -> List[QueryDatum]:
        if ns_parts is None:
            ns_parts = []
        query_data = []
        query_sql_strs = query_name_definition_pattern.split(sql)

        # Drop the first item in the split. It is anything above the first query definition.
        # This may be SQL comments or empty lines.
        # See: https://github.com/nackjicholson/aiosql/issues/35
        for query_sql_str in query_sql_strs[1:]:
            query_data.append(self._make_query_datum(query_sql_str, ns_parts))
        return query_data

    def load_query_data_from_file(
        self, file_path: Path, ns_parts: Optional[List] = None
    ) -> List[QueryDatum]:
        if ns_parts is None:
            ns_parts = []

        with file_path.open() as fp:
            return self.load_query_data_from_sql(fp.read(), ns_parts)

    def load_query_data_from_dir_path(self, dir_path) -> QueryDataTree:
        if not dir_path.is_dir():
            raise ValueError(f"The path {dir_path} must be a directory")

        def _recurse_load_query_data_tree(path, ns_parts=None):
            if ns_parts is None:
                ns_parts = []

            query_data_tree = {}
            for p in path.iterdir():
                if p.is_file() and p.suffix != ".sql":
                    continue
                elif p.is_file() and p.suffix == ".sql":
                    for query_datum in self.load_query_data_from_file(p, ns_parts):
                        query_data_tree[query_datum.query_name] = query_datum
                elif p.is_dir():
                    query_data_tree[p.name] = _recurse_load_query_data_tree(p, ns_parts + [p.name])
                else:
                    # This should be practically unreachable.
                    raise SQLLoadException(f"The path must be a directory or file, got {p}")
            return query_data_tree

        return _recurse_load_query_data_tree(dir_path)
