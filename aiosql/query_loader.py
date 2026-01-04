import re
import inspect
from pathlib import Path
from typing import Type, Sequence, Any

from .utils import SQLParseException, SQLLoadException, VAR_REF, VAR_REF_DOT, log
from .types import QueryDatum, QueryDataTree, SQLOperationType, DriverAdapterProtocol

# identifies name definition comments
_QUERY_DEF = re.compile(r"--\s*name\s*:\s*")

# identifies record class definition comments
_RECORD_DEF = re.compile(r"--\s*record_class\s*:\s*(\w+)\s*")

# extract a valid query name followed by an optional operation spec
# FIXME this accepts "1st" but seems to reject "é"
_NAME_OP = re.compile(
    # query name
    r"^(?P<name>\w+)\s*"
    # optional list of parameters (foo, bla) or ()
    r"(|\((?P<params>(\s*|\s*\w+\s*(,\s*\w+\s*)*))\))\s*"
    # operation, empty for simple select
    r"(?P<op>(|\^|\$|!|<!|\*!|#))$"
)

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

# extracting comments requires some kind of scanner
_UNCOMMENT = re.compile(
    # single quote strings
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    # double quote strings
    r'(?P<dquote>"(""|[^"])+")|'
    # one-line comment
    r"(?P<oneline>--.*?$)|"
    # multiline comments, excluding SQL hints
    r"|(?P<multiline>/\*(?!\+[\s\S]*?\*/)[\s\S]*?\*/)",
    re.DOTALL | re.MULTILINE,
)


def _remove_ml_comments(code: str) -> str:
    """Remove /* ... */ comments from code"""
    # identify commented regions to be removed
    rm = []
    for m in _UNCOMMENT.finditer(code):
        ml = m.groupdict()["multiline"]
        if ml:
            rm.append(m.span())
    # keep whatever else
    ncode, current = "", 0
    for start, end in rm:
        ncode += code[current:start]
        current = end
    # get tail
    ncode += code[current:]
    return ncode


def _preprocess_object_attributes(attribute, sql):
    """Substitute o.a by o<attribute>a and keep track of variables."""

    attributes = {}

    def _replace(m):
        gd = m.groupdict()
        if gd["dquote"] is not None:
            return gd["dquote"]
        elif gd["squote"] is not None:
            return gd["squote"]
        else:
            var, att = gd["var_name"].split(".", 1)
            var_name = var + attribute + att
            if var not in attributes:
                attributes[var] = {}
            if att not in attributes[var]:
                attributes[var][att] = var_name
            return f"{gd['lead']}:{var_name}"

    sql = VAR_REF_DOT.sub(_replace, sql)

    return sql, attributes


class QueryLoader:
    """Load Queries.

    This class holds the various utilities to read SQL files and build
    QueryDatum, which will be transformed as functions in Queries.

    - :param driver_adapter: driver name or class.
    - :param record_classes: nothing of dict.
    - :param attribute: string to insert in place of ``.``.
    - :param mandatory_parameters: whether params are required.
    """

    def __init__(
        self,
        driver_adapter: DriverAdapterProtocol,
        record_classes: dict[str, Any]|None,
        attribute: str|None = None,
        mandatory_parameters: bool = True,
    ):
        self._driver_adapter = driver_adapter
        self._record_classes = record_classes if record_classes is not None else {}
        self._attribute = attribute
        self._mandatory_parameters = mandatory_parameters

    def _make_query_datum(
        self,
        query: str,
        ns_parts: list[str],
        floc: tuple[Path|str, int],
    ) -> QueryDatum:
        """Build a query datum.

        - :param query: the spec and name (``query-name(…)!\n-- comments\nSQL;\n``)
        - :param ns_parts: name space parts, i.e. subdirectories of loaded files
        - :param floc: file name and lineno the query was extracted from
        """
        lines = [line.rstrip() for line in query.strip().splitlines()]
        qname, qop, qsig = self._get_name_op(lines[0], floc)
        if re.search(r"[^A-Za-z0-9_]", qname):
            log.warning(f"non ASCII character in query name: {qname}")
        if len(lines) <= 1:
            raise SQLParseException(f"empty query for: {qname} at {floc[0]}:{floc[1]}")
        record_class = self._get_record_class(lines[1])
        sql, doc = self._get_sql_doc(lines[2 if record_class else 1 :])
        if re.search("(?s)^[\t\n\r ;]*$", sql):
            raise SQLParseException(f"empty sql for: {qname} at {floc[0]}:{floc[1]}")
        signature = self._build_signature(sql, qname, qsig)
        query_fqn = ".".join(ns_parts + [qname])
        if self._attribute:  # :u.a -> :u__a, **after** signature generation
            sql, attributes = _preprocess_object_attributes(self._attribute, sql)
        else:  # pragma: no cover
            attributes = None
        sql = self._driver_adapter.process_sql(query_fqn, qop, sql)
        return QueryDatum(query_fqn, doc, qop, sql, record_class, signature, floc, attributes, qsig)

    def _get_name_op(self, text: str, floc: tuple[Path|str, int]) -> tuple[str, SQLOperationType, list[str]|None]:
        """Extract name, parameters and operation from spec."""
        qname_spec = text.replace("-", "_")
        matched = _NAME_OP.match(qname_spec)
        if not matched or _BAD_PREFIX.match(qname_spec):
            raise SQLParseException(f'invalid query name and operation spec at {floc[0]}:{floc[1]} on "{qname_spec}"')
        nameop = matched.groupdict()
        # extract operation
        operation = _OP_TYPES[nameop["op"]]
        # extract parameters
        params, rawparams = None, nameop["params"]
        if self._mandatory_parameters and rawparams is None and nameop["op"] not in ("#", "*!", "<!"):
            raise SQLParseException(f'missing mandatory parameter list at {floc[0]}:{floc[1]} on "{qname_spec}", '
                                    'use "mandatory_parameters=False" to allow')
        if rawparams is not None:
            params = [p.strip() for p in rawparams.split(",")]
            if params == ['']:  # handle "( )"
                params = []
        # sanity check for scripts
        if params and nameop["op"] == "#":
            raise SQLParseException(f'cannot use named parameters in SQL script at {floc[0]}:{floc[1]} on "{qname_spec}"')
        return nameop["name"], operation, params

    def _get_record_class(self, text: str) -> Type|None:
        """Extract record class from spec."""
        rc_match = _RECORD_DEF.match(text)
        rc_name = rc_match.group(1) if rc_match else None
        # TODO: Probably will want this to be a class, marshal in, and marshal out
        return self._record_classes.get(rc_name) if isinstance(rc_name, str) else None

    def _get_sql_doc(self, lines: Sequence[str]) -> tuple[str, str]:
        """Separate SQL-comment documentation and SQL code."""
        doc, sql = "", ""
        for line in lines:
            doc_match = _SQL_COMMENT.match(line)
            if doc_match:
                doc += doc_match.group(1) + "\n"
            else:
                sql += line + "\n"

        return sql.strip(), doc.rstrip()

    def _build_signature(self, sql: str, qname: str, sig: list[str]|None) -> inspect.Signature:
        """Return signature object for generated dynamic function."""
        # FIXME what about the connection?!
        params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        names = set()
        for match in VAR_REF.finditer(sql):
            gd = match.groupdict()
            if gd["squote"] or gd["dquote"]:
                continue
            name = gd["var_name"]
            if name.isdigit() or name in names:
                continue
            if sig is not None:  # optional parameter declarations
                if name not in sig:
                    raise SQLParseException(f"undeclared parameter name in query {qname}: {name}")
            names.add(name)
            params.append(
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                )
            )
        if sig is not None and len(sig) != len(names):
            unused = sorted(n for n in sig if n not in names)
            raise SQLParseException(f"unused declared parameter in query {qname}: {unused}")
        return inspect.Signature(parameters=params)

    def load_query_data_from_sql(
        self, sql: str, ns_parts: list[str], fname: Path|str = "<unknown>"
    ) -> list[QueryDatum]:
        """Load queries from a string."""
        usql = _remove_ml_comments(sql)
        qdefs = _QUERY_DEF.split(usql)
        # FIXME lineno is from the uncommented file
        lineno = 1 + qdefs[0].count("\n")
        data = []
        # first item is anything before the first query definition, drop it!
        for qdef in qdefs[1:]:
            data.append(self._make_query_datum(qdef, ns_parts, (fname, lineno)))
            lineno += qdef.count("\n")
        return data

    def load_query_data_from_file(
        self, path: Path, ns_parts: list[str] = [], encoding=None
    ) -> list[QueryDatum]:
        """Load queries from a file."""
        return self.load_query_data_from_sql(path.read_text(encoding=encoding), ns_parts, path)

    def load_query_data_from_dir_path(
        self, dir_path, ext=(".sql",), encoding=None
    ) -> QueryDataTree:
        """Load queries from a directory."""
        if not dir_path.is_dir():
            raise ValueError(f"The path {dir_path} must be a directory")

        def _recurse_load_query_data_tree(path, ns_parts=[], ext=(".sql",), encoding=None):
            query_data_tree = {}
            for p in path.iterdir():
                if p.is_file():
                    if p.suffix not in ext:
                        continue
                    for query_datum in self.load_query_data_from_file(
                        p, ns_parts, encoding=encoding
                    ):
                        query_data_tree[query_datum.query_name] = query_datum
                elif p.is_dir():
                    query_data_tree[p.name] = _recurse_load_query_data_tree(
                        p, ns_parts + [p.name], ext=ext, encoding=encoding
                    )
                else:  # pragma: no cover
                    # This should be practically unreachable.
                    raise SQLLoadException(f"The path must be a directory or file, got {p}")
            return query_data_tree

        return _recurse_load_query_data_tree(dir_path, ext=ext, encoding=encoding)
