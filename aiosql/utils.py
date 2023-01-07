# use re2 if available.
# FIXME strange issue on debian buster with py3.7 apache wsgi flask… loading re2 "freezes" the process
try:
    import re2 as re
except ModuleNotFoundError:  # pragma: no cover
    import re  # type: ignore

# FIXME to be improved
VAR_REF = re.compile(
    # NOTE probably pg specific?
    r'(?P<dblquote>"(""|[^"])+")|'
    # FIXME mysql/mariadb use backslash escapes
    r"(?P<quote>\'(\'\'|[^\'])*\')|"
    # FIXME fails if variables are separated by only one char: :v1+:v2
    # because lead and trail overlap
    r"(?P<lead>[^:]):(?P<var_name>[\w-]+)(?P<trail>[^:]?)"
)
"""Pattern to identifies colon-variables in SQL code"""


class SQLLoadException(Exception):
    """Raised when there is a problem loading SQL content from a file or directory"""

    pass


class SQLParseException(Exception):
    """Raised when there was a problem parsing the aiosql comment annotations in SQL"""

    pass
