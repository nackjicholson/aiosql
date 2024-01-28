import re
import logging

# FIXME to be improved
VAR_REF = re.compile(
    # NOTE probably pg specific?
    r'(?P<dquote>"(""|[^"])+")|'
    # FIXME mysql/mariadb use backslash escapes
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    # NOTE beware of overlapping re
    r"(?P<lead>[^:]):(?P<var_name>[\w-]+)(?=[^:]?)"
)
"""Pattern to identifies colon-variables (aka _named_ style) in SQL code"""

log = logging.getLogger("aiosql")
# log.setLevel(logging.DEBUG)


class SQLLoadException(Exception):
    """Raised when there is a problem loading SQL content from a file or directory"""

    pass


class SQLParseException(Exception):
    """Raised when there was a problem parsing the aiosql comment annotations in SQL"""

    pass
