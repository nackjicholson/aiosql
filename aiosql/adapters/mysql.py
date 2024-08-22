from .pyformat import PyFormatAdapter


class BrokenMySQLAdapter(PyFormatAdapter):
    """
    Work around PyMySQL and MySQLDB mishandling of empty parameters
    and lack of willingness to fix the issue.

    See: https://github.com/PyMySQL/PyMySQL/issues/1059
    """

    def select(self, conn, query_name, sql, parameters, record_class=None):
        return super().select(conn, query_name, sql, parameters or [], record_class)

    def select_one(self, conn, query_name, sql, parameters, record_class=None):
        return super().select_one(conn, query_name, sql, parameters or [], record_class)

    def select_value(self, conn, query_name, sql, parameters):
        return super().select_value(conn, query_name, sql, parameters or [])

    def insert_update_delete(self, conn, query_name, sql, parameters):
        return super().insert_update_delete(conn, query_name, sql, parameters or [])

    # only called for mariadb, as mysql does not implement RETURNING
    def insert_returning(self, conn, query_name, sql, parameters):  # pragma: no cover
        return super().insert_returning(conn, query_name, sql, parameters or [])

    # left out with parameters: insert_update_delete_many, select_cursor
