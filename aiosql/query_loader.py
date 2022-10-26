import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type, Sequence, Any

from .utils import SQLParseException, SQLLoadException, VAR_REF, re
from .types import QueryDatum, QueryDataTree, SQLOperationType, DriverAdapterProtocol

# identifies name definition comments
_QUERY_DEF = re.compile(r"--\s*name\s*:\s*")

# identifies record class definition comments
_RECORD_DEF = re.compile(r"--\s*record_class\s*:\s*(\w+)\s*")

# extract a valid query name followed by an optional operation spec
# FIXME this accepts "1st" but seems to reject "é"
_NAME_OP = re.compile(r"^(\w+)(|\^|\$|!|<!|\*!|#)$")

# forbid numbers as first character
_BAD_PREFIX = re.compile(r"^\d")

# get SQL comment contents
_SQL_COMMENT = re.compile(r"\s*--\s*(.*)$")

# map operation suffixes to their type
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
    def __init__(
        self, driver_adapter: DriverAdapterProtocol, record_classes: Optional[Dict[str, Any]]
    ):
        self.driver_adapter = driver_adapter
        self.record_classes = record_classes if record_classes is not None else {}

    def _make_query_datum(
        self, query: str, ns_parts: List[str], floc: Optional[Tuple[Path, int]] = None
    ) -> QueryDatum:
        # Build a query datum
        # - query: the spec and name ("query-name!\n-- comments\nSQL;\n")
        # - ns_parts: name space parts, i.e. subdirectories of loaded files
        # - floc: file name and lineno the query was extracted from
        lines = [line.strip() for line in query.strip().splitlines()]
        qname, qop = self._get_name_op(lines[0])
        record_class = self._get_record_class(lines[1])
        sql, doc = self._get_sql_doc(lines[2 if record_class else 1 :])
        signature = self._build_signature(sql)
        query_fqn = ".".join(ns_parts + [qname])
        sql = self.driver_adapter.process_sql(query_fqn, qop, sql)
        return QueryDatum(query_fqn, doc, qop, sql, record_class, signature, floc)

    def _get_name_op(self, text: str) -> Tuple[str, SQLOperationType]:
        qname_spec = text.replace("-", "_")
        nameop = _NAME_OP.match(qname_spec)
        if not nameop or _BAD_PREFIX.match(qname_spec):
            raise SQLParseException(f'invalid query name and operation spec: "{qname_spec}"')
        qname, qop = nameop.group(1, 2)
        return qname, _OP_TYPES[qop]

    def _get_record_class(self, text: str) -> Optional[Type]:
        rc_match = _RECORD_DEF.match(text)
        rc_name = rc_match.group(1) if rc_match else None
        # TODO: Probably will want this to be a class, marshal in, and marshal out
        return self.record_classes.get(rc_name)

    def _get_sql_doc(self, lines: Sequence[str]) -> Tuple[str, str]:
        doc, sql = "", ""
        for line in lines:
            doc_match = _SQL_COMMENT.match(line)
            if doc_match:
                doc += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        return sql.strip(), doc.rstrip()

    def _build_signature(self, sql: str) -> inspect.Signature:
        params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        names = set()
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
        return inspect.Signature(parameters=params)

    def load_query_data_from_sql(
        self, sql: str, ns_parts: List[str] = [], fname: Optional[Path] = None
    ) -> List[QueryDatum]:
        qdefs = _QUERY_DEF.split(sql)
        lineno = 1 + qdefs[0].count("\n")
        data = []
        # first item is anything before the first query definition, drop it!
        for qdef in qdefs[1:]:
            data.append(self._make_query_datum(qdef, ns_parts, (fname, lineno) if fname else None))
            lineno += qdef.count("\n")
        return data

    def load_query_data_from_file(self, path: Path, ns_parts: List[str] = []) -> List[QueryDatum]:
        return self.load_query_data_from_sql(path.read_text(), ns_parts, path)

    def load_query_data_from_dir_path(self, dir_path, ext=(".sql",)) -> QueryDataTree:
        if not dir_path.is_dir():
            raise ValueError(f"The path {dir_path} must be a directory")

        def _recurse_load_query_data_tree(path, ns_parts=[], ext=(".sql",)):
            query_data_tree = {}
            for p in path.iterdir():
                if p.is_file():
                    if p.suffix not in ext:
                        continue
                    for query_datum in self.load_query_data_from_file(p, ns_parts):
                        query_data_tree[query_datum.query_name] = query_datum
                elif p.is_dir():
                    query_data_tree[p.name] = _recurse_load_query_data_tree(
                        p, ns_parts + [p.name], ext=ext
                    )
                else:  # pragma: no cover
                    # This should be practically unreachable.
                    raise SQLLoadException(f"The path must be a directory or file, got {p}")
            return query_data_tree

        return _recurse_load_query_data_tree(dir_path, ext=ext)
