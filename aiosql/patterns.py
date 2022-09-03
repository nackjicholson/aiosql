# use re2 if available.
# FIXME strange issue on debian buster with py3.7 apache wsgi flask… loading re2 "freezes" aiosql
try:
    import re2 as re
except ModuleNotFoundError:  # pragma: no cover
    import re  # type: ignore

VAR_REF = re.compile(
    r'(?P<dblquote>"[^"]+")|'
    r"(?P<quote>\'[^\']*\')|"
    r"(?P<lead>[^:]):(?P<var_name>[\w-]+)(?P<trail>[^:]?)"
)
"""
Pattern: Identifies variables in SQL code.
"""
