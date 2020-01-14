from contextlib import contextmanager

from ..record import assign_record_class

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
    def select(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        results = cur.fetchall()
        if record_class is not None:
            column_names = [c[0] for c in cur.description]
            results = assign_record_class(results, column_names, record_class)
        cur.close()
        return results

    @staticmethod
    def select_one(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        result = cur.fetchone()
        if result is not None and record_class is not None:
            column_names = [c[0] for c in cur.description]
            result = assign_record_class(results, column_names, record_class, True)
        cur.close()
        return result

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
