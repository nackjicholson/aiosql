from .pyformat import PyFormatAdapter


class BrokenMySQLAdapter(PyFormatAdapter):
    """
    Work around PyMySQL and MySQLDB mishandling of empty parameters.

    See: https://github.com/PyMySQL/PyMySQL/issues/1059
    """

    def _params(self, p):
        return p if p != () else None

    def select(self, conn, name, sql, p, rc=None):
        return super().select(conn, name, sql, self._params(p), rc)

    def select_one(self, conn, name, sql, p, rc=None):
        return super().select_one(conn, name, sql, self._params(p), rc)

    def select_value(self, conn, name, sql, p):
        return super().select_value(conn, name, sql, self._params(p))

    def insert_update_delete(self, conn, name, sql, p):
        return super().insert_update_delete(conn, name, sql, self._params(p))
