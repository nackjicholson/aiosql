from contextlib import contextmanager


class GenericAdapter:
    """
    Generic AioSQL Adapter suitable for `named` parameter style and no with support.
    """

    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        return sql

    @staticmethod
    def select(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        try:
            cur.execute(sql, parameters)
            results = cur.fetchall()
            if record_class is not None and len(results) > 0:
                column_names = [c[0] for c in cur.description]
                results = [record_class(**dict(zip(column_names, row))) for row in results]
        finally:
            cur.close()
        return results

    @staticmethod
    def select_one(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                result = record_class(**dict(zip(column_names, result)))
        finally:
            cur.close()
        return result

    @staticmethod
    def select_value(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
        finally:
            cur.close()
        return result[0] if result else None

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
        cur = conn.cursor()
        cur.execute(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    @staticmethod
    def insert_update_delete_many(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.executemany(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    @staticmethod
    def insert_returning(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        res = cur.fetchone()
        cur.close()
        return res[0] if res and len(res) == 1 else res

    @staticmethod
    def execute_script(conn, sql):
        cur = conn.cursor()
        cur.execute(sql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        cur.close()
        return msg
