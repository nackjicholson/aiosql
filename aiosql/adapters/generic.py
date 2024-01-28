from contextlib import contextmanager
from typing import List


class GenericAdapter:
    """
    Generic AioSQL Adapter suitable for `named` parameter style and no with support.

    This class also serves as the base class for other adapters.
    """

    def __init__(self, driver=None):
        self._driver = driver

    def process_sql(self, _query_name, _op_type, sql):
        """Preprocess SQL query."""
        return sql

    def _cursor(self, conn):
        """Get a cursor from a connection."""
        return conn.cursor()

    def select(self, conn, _query_name: str, sql: str, parameters, record_class=None):
        """Handle a relation-returning SELECT (no suffix)."""
        column_names: List[str] = []
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            if record_class is None:
                for row in cur:
                    yield row
            else:
                first = True
                for row in cur:
                    if first:  # only get description on the fly, for apsw
                        column_names = [c[0] for c in cur.description]
                        first = False
                    yield record_class(**dict(zip(column_names, row)))
        finally:
            cur.close()

    def select_one(self, conn, _query_name, sql, parameters, record_class=None):
        """Handle a tuple-returning (one row) SELECT (``^`` suffix).

        Return None if empty."""
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                # this fails if result is not a list or tuple
                result = record_class(**dict(zip(column_names, result)))
        finally:
            cur.close()
        return result

    def select_value(self, conn, _query_name, sql, parameters):
        """Handle a scalar-returning (one value) SELECT (``$`` suffix).

        Return None if empty."""
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result:
                if isinstance(result, (list, tuple)):
                    return result[0]
                elif isinstance(result, dict):
                    return next(iter(result.values()))
                else:  # pragma: no cover
                    raise Exception(f"unexpected value type: {type(result)}")
            else:
                return None
        finally:
            cur.close()

    @contextmanager
    def select_cursor(self, conn, _query_name, sql, parameters):
        """Return the raw cursor after a SELECT exec."""
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        try:
            yield cur
        finally:
            cur.close()

    def insert_update_delete(self, conn, _query_name, sql, parameters):
        """Handle affected row counts (INSERT UPDATE DELETE) (``!`` suffix)."""
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    def insert_update_delete_many(self, conn, _query_name, sql, parameters):
        """Handle affected row counts (INSERT UPDATE DELETE) (``*!`` suffix)."""
        cur = self._cursor(conn)
        cur.executemany(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    # FIXME this made sense when SQLite had no RETURNING prefix (v3.35, 2021-03-12)
    def insert_returning(self, conn, _query_name, sql, parameters):
        """Special case for RETURNING (``<!`` suffix) with SQLite."""
        # very similar to select_one but the returned value
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        res = cur.fetchone()
        cur.close()
        return res[0] if res and len(res) == 1 else res

    def execute_script(self, conn, sql):
        """Handle an SQL script (``#`` suffix)."""
        cur = self._cursor(conn)
        cur.execute(sql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        cur.close()
        return msg
