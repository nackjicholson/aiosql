from .pyformat import PyFormatAdapter


class BrokenMySQLAdapter(PyFormatAdapter):
    """
    Work around PyMySQL and MySQLDB mishandling of empty parameters.

    See: https://github.com/PyMySQL/PyMySQL/issues/1059
    """

    def select(self, conn, name, sql, params, rc=None):
        return super().select(conn, name, sql, params or None, rc)

    def select_one(self, conn, name, sql, params, rc=None):
        return super().select_one(conn, name, sql, params or None, rc)

    def select_value(self, conn, name, sql, params):
        return super().select_value(conn, name, sql, params or None)

    def insert_update_delete(self, conn, name, sql, params):
        return super().insert_update_delete(conn, name, sql, params or None)

    # only called for mariadb, as mysql does not implement RETURNING
    def insert_returning(self, conn, name, sql, params):  # pragma: no cover
        return super().insert_returning(conn, name, sql, params or None)

    # left out with params: insert_update_delete_many, select_cursor
