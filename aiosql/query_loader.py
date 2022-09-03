import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type, Sequence, Union

from .exceptions import SQLParseException, SQLLoadException
from .types import QueryDatum, QueryDataTree, SQLOperationType, DriverAdapterProtocol
from .patterns import VAR_REF

# use re2 if available.
# FIXME strange issue on debian buster with py3.7 apache wsgi flask… loading re2 "freezes" aiosql
try:
    import re2 as re
except ModuleNotFoundError:  # pragma: no cover
    import re  # type: ignore

_QUERY_DEF = re.compile(r"--\s*name\s*:\s*")
"""
Pattern: Identifies name definition comments.
"""

_RECORD_DEF = re.compile(r"--\s*record_class\s*:\s*(\w+)\s*")
"""
Pattern: Identifies record_class definition comments.
"""

# FIXME this accepts "1st" but seems to reject "é"
_NAME_OP = re.compile(r"^(\w+)(|\^|\$|!|<!|\*!|#)$")
"""
Pattern: Enforces names are valid python variable names followed by operation.
"""

_BAD_PREFIX = re.compile(r"^\d")
"""
Pattern: not these as a first query name character.
"""

_SQL_COMMENT = re.compile(r"\s*--\s*(.*)$")
"""
Pattern: Identifies SQL comments.
"""

_OP_TYPES = {
    "<!": SQLOperationType.INSERT_RETURNING,
    "*!": SQLOperationType.INSERT_UPDATE_DELETE_MANY,
    "!": SQLOperationType.INSERT_UPDATE_DELETE,
    "#": SQLOperationType.SCRIPT,
    "^": SQLOperationType.SELECT_ONE,
    "$": SQLOperationType.SELECT_VALUE,
    "": SQLOperationType.SELECT,
}


class QueryLoader:
    def __init__(self, driver_adapter: DriverAdapterProtocol, record_classes: Optional[Dict]):
        self.driver_adapter = driver_adapter
        self.record_classes = record_classes if record_classes is not None else {}

    def _make_query_datum(
        self, query: str, ns_parts: List[str], fname: Optional[Path] = None
    ) -> QueryDatum:
        # Build a query datum
        # - query: the spec and name ("query-name!\n-- comments\nSQL;\n")
        # - ns_parts: name space parts, i.e. subdirectories of loaded files
        # - fname: name of file the query was extracted from
        lines = [line.strip() for line in query.strip().splitlines()]
        optype, qname = self._extract_operation_type(lines[0])
        record_class = self._extract_record_class(lines[1])
        line_offset = 2 if record_class else 1
        doc, sql = self._extract_docstring(lines[line_offset:])
        signature = self._extract_signature(sql)
        query_fqn = ".".join(ns_parts + [qname])
        sql = self.driver_adapter.process_sql(query_fqn, optype, sql)
        return QueryDatum(query_fqn, doc, optype, sql, record_class, signature, fname)

    @staticmethod
    def _extract_operation_type(text: str) -> Tuple[SQLOperationType, str]:
        query_name = text.replace("-", "_")
        nameop = _NAME_OP.match(query_name)
        if not nameop or _BAD_PREFIX.match(query_name):
            raise SQLParseException(f'invalid query name and operation spec: "{query_name}"')
        query_name, operation = nameop.group(1, 2)
        assert operation in _OP_TYPES
        operation_type = _OP_TYPES[operation]

        return operation_type, query_name

    def _extract_record_class(self, text: str) -> Optional[Type]:
        rc_match = _RECORD_DEF.match(text)
        record_class_name = rc_match.group(1) if rc_match else None
        # TODO: Probably will want this to be a class, marshal in, and marshal out
        record_class = self.record_classes.get(record_class_name)
        return record_class

    @staticmethod
    def _extract_docstring(lines: Sequence[str]) -> Tuple[str, str]:
        doc, sql = "", ""
        for line in lines:
            doc_match = _SQL_COMMENT.match(line)
            if doc_match:
                doc += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        return doc.rstrip(), sql.strip()

    @staticmethod
    def _extract_signature(sql: str) -> Optional[inspect.Signature]:
        params = []
        names = set()
        self = inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for match in VAR_REF.finditer(sql):
            gd = match.groupdict()
            if gd["quote"] or gd["dblquote"]:
                continue
            name = gd["var_name"]
            if name.isdigit() or name in names:
                continue
            names.add(name)
            params.append(
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                )
            )
        return inspect.Signature(parameters=[self] + params) if params else None

    def load_query_data_from_sql(
        self, sql: Union[str, Path], ns_parts: Optional[List] = None
    ) -> List[QueryDatum]:
        sql_fname: Optional[Path] = None
        if isinstance(sql, Path):
            with sql.open() as fp:
                sql_str = fp.read()
            sql_fname = sql
        else:
            sql_str = sql

        if ns_parts is None:
            ns_parts = []
        query_data = []
        query_sql_strs = _QUERY_DEF.split(sql_str)

        # Drop the first item in the split. It is anything above the first query definition.
        # This may be SQL comments or empty lines.
        # See: https://github.com/nackjicholson/aiosql/issues/35
        for query_sql_str in query_sql_strs[1:]:
            query_data.append(self._make_query_datum(query_sql_str, ns_parts, sql_fname))
        return query_data

    def load_query_data_from_file(
        self, file_path: Path, ns_parts: Optional[List] = None
    ) -> List[QueryDatum]:
        return self.load_query_data_from_sql(file_path, ns_parts)

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
                else:  # pragma: no cover
                    # This should be practically unreachable.
                    raise SQLLoadException(f"The path must be a directory or file, got {p}")
            return query_data_tree

        return _recurse_load_query_data_tree(dir_path)
