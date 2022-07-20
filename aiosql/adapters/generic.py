from contextlib import contextmanager


class GenericAdapter:
    """
    Generic AioSQL Adapter suitable for `named` parameter style and no with support.
    """

    def __init__(self, driver=None):
        self._driver = driver

    def process_sql(self, _query_name, _op_type, sql):
        """Preprocess SQL query."""
        return sql

    def _cursor(self, conn):
        """Get a cursor from a connection."""
        return conn.cursor()

    def select(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            results = cur.fetchall()
            if record_class is not None and len(results) > 0:
                column_names = [c[0] for c in cur.description]
                results = [record_class(**dict(zip(column_names, row))) for row in results]
        finally:
            cur.close()
        return results

    def select_one(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                result = record_class(**dict(zip(column_names, result)))
        finally:
            cur.close()
        return result

    def select_value(self, conn, _query_name, sql, parameters):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
        finally:
            cur.close()
        return result[0] if result else None

    @contextmanager
    def select_cursor(self, conn, _query_name, sql, parameters):
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        try:
            yield cur
        finally:
            cur.close()

    def insert_update_delete(self, conn, _query_name, sql, parameters):
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    def insert_update_delete_many(self, conn, _query_name, sql, parameters):
        cur = self._cursor(conn)
        cur.executemany(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    def insert_returning(self, conn, _query_name, sql, parameters):
        # very similar to select_one but the returned value
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        res = cur.fetchone()
        cur.close()
        return res[0] if res and len(res) == 1 else res

    def execute_script(self, conn, sql):
        cur = self._cursor(conn)
        cur.execute(sql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        cur.close()
        return msg
