from contextlib import contextmanager


class SQLite3DriverAdapter:
    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        """Pass through function because the ``sqlite3`` driver already handles the :var_name
        "named style" syntax used by aiosql variables. Note, it will also accept "qmark style"
        variables.

        Args:
            _query_name (str): The name of the sql query. Unused.
            _op_type (aiosql.SQLOperationType): The type of SQL operation performed by the sql.
            sql (str): The sql as written before processing.

        Returns:
            str: Original SQL text unchanged.
        """
        return sql

    @staticmethod
    def select(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        results = cur.fetchall()
        cur.close()
        return results

    @staticmethod
    @contextmanager
    def select_cursor(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        try:
            yield cur
        finally:
            cur.close()

    @staticmethod
    def insert_update_delete(conn, _query_name, sql, parameters):
        conn.execute(sql, parameters)

    @staticmethod
    def insert_update_delete_many(conn, _query_name, sql, parameters):
        conn.executemany(sql, parameters)

    @staticmethod
    def insert_returning(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        results = cur.lastrowid
        cur.close()
        return results

    @staticmethod
    def execute_script(conn, sql):
        conn.executescript(sql)
