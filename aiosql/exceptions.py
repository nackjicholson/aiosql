class SQLLoadException(Exception):
    """Raised when there is a problem loading SQL content from a file or directory."""

    pass


class SQLParseException(Exception):
    """Raised when there was a problem parsing the aiosql comment annotations in SQL"""

    pass
