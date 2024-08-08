import re
import logging

# FIXME to be improved
VAR_REF = re.compile(
    # NOTE probably pg specific?
    r'(?P<dquote>"(""|[^"])+")|'
    # FIXME mysql/mariadb use backslash escapes
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    # NOTE beware of overlapping re
    r"(?P<lead>[^:]):(?P<var_name>\w+)(?=[^:]?)"
)
"""Pattern to identify colon-variables (aka _named_ style) in SQL code"""

# NOTE see comments above
VAR_REF_DOT = re.compile(
    r'(?P<dquote>"(""|[^"])+")|'
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    r"(?P<lead>[^:]):(?P<var_name>\w+\.\w+)(?=[^:]?)"
)
"""Pattern to identify colon-variables with a simple attribute in SQL code."""

log = logging.getLogger("aiosql")
"""Shared package logging."""
# log.setLevel(logging.DEBUG)


class SQLLoadException(Exception):
    """Raised when there is a problem loading SQL content from a file or directory"""

    pass


class SQLParseException(Exception):
    """Raised when there was a problem parsing the aiosql comment annotations in SQL"""

    pass
