from .generic import GenericAdapter


class DuckDBAdapter(GenericAdapter):
    """DuckDB Adapter"""
    convert_row_to_dict: bool = False
    """Converts the default tuple response to a dict."""

    def __init__(self, driver=None, cursor_as_dict: bool = False):
        super().__init__(driver=driver)
        self.convert_row_to_dict = cursor_as_dict

    def insert_returning(self, conn, _query_name, sql, parameters):
        # very similar to select_one but the returned value
        cur = self._cursor(conn)
        cur.execute(sql, parameters)
        # we have to use fetchall instead of fetchone for now due to this:
        # https://github.com/duckdb/duckdb/issues/6008
        res = cur.fetchall()
        cur.close()
        if isinstance(res, list):
            res = res[0]
        return res[0] if res and len(res) == 1 else res

    def select(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            if record_class is None:

                first = True
                for row in cur.fetchall():
                    if first:  # get column names on the fly
                        column_names = [c[0] for c in cur.description]
                        first = False
                    if self.convert_row_to_dict:
                        yield dict(zip(column_names, row))
                    else:
                        yield row
            else:
                first = True
                for row in cur.fetchall():
                    if first:  # only get description on the fly, for apsw
                        column_names = [c[0] for c in cur.description]
                        first = False
                    yield record_class(**dict(zip(column_names, row)))
        finally:
            cur.close()

    def select_one(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                result = record_class(**dict(zip(column_names, result)))
            elif result is not None and self.convert_row_to_dict:
                column_names = [c[0] for c in cur.description]
                result = dict(zip(column_names, result))
        finally:
            cur.close()
        return result
