from .pyformat import PyFormatAdapter


class BrokenMySQLAdapter(PyFormatAdapter):
    """
    Work around PyMySQL and MySQLDB mishandling of empty parameters.

    See: https://github.com/PyMySQL/PyMySQL/issues/1059
    """

    def select(self, conn, name, sql, parameters, record_class=None):
        return super().select(conn, name, sql, parameters or None, record_class)

    def select_one(self, conn, name, sql, parameters, record_class=None):
        return super().select_one(conn, name, sql, parameters or None, record_class)

    def select_value(self, conn, name, sql, parameters):
        return super().select_value(conn, name, sql, parameters or None)

    def insert_update_delete(self, conn, name, sql, parameters):
        return super().insert_update_delete(conn, name, sql, parameters or None)

    # only called for mariadb, as mysql does not implement RETURNING
    def insert_returning(self, conn, name, sql, parameters):  # pragma: no cover
        return super().insert_returning(conn, name, sql, parameters or None)

    # left out with parameters: insert_update_delete_many, select_cursor
