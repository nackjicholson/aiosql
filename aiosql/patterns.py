# use re2 if available.
try:
    import re2 as re
except ModuleNotFoundError:  # pragma: no cover
    import re  # type: ignore

query_name_definition_pattern = re.compile(r"--\s*name\s*:\s*")
"""
Pattern: Identifies name definition comments.
"""

query_record_class_definition_pattern = re.compile(r"--\s*record_class\s*:\s*(\w+)\s*")
"""
Pattern: Identifies record_class definition comments.
"""

empty_pattern = re.compile(r"^\s*$")
"""
Pattern: Identifies empty lines.
"""

valid_query_name_pattern = re.compile(r"^\w+$")
"""
Pattern: Enforces names are valid python variable names.
"""

doc_comment_pattern = re.compile(r"\s*--\s*(.*)$")
"""
Pattern: Identifies SQL comments.
"""

var_pattern = re.compile(
    r'(?P<dblquote>"[^"]+")|'
    r"(?P<quote>\'[^\']*\')|"
    r"(?P<lead>[^:]):(?P<var_name>[\w-]+)(?P<trail>[^:]?)"
)
"""
Pattern: Identifies variable definitions in SQL code.
"""
