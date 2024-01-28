from .generic import GenericAdapter
from ..utils import VAR_REF
from typing import List


def _colon_to_dollar(match):
    """Convert 'WHERE :id = 1' to 'WHERE $id = 1'."""
    gd = match.groupdict()
    if gd["dquote"] is not None:
        return gd["dquote"]
    elif gd["squote"] is not None:
        return gd["squote"]
    else:
        return f'{gd["lead"]}${gd["var_name"]}'


class DuckDBAdapter(GenericAdapter):
    """DuckDB Adapter"""

    def __init__(self, driver=None, cursor_as_dict: bool = False):
        super().__init__(driver=driver)
        # whether to converts the default tuple response to a dict.
        self._convert_row_to_dict = cursor_as_dict

    def process_sql(self, _query_name, _op_type, sql):
        return VAR_REF.sub(_colon_to_dollar, sql)

    def insert_returning(self, conn, _query_name, sql, parameters):  # pragma: no cover
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

    def select(self, conn, _query_name: str, sql: str, parameters, record_class=None):
        column_names: List[str] = []
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            if record_class is None:
                first = True
                for row in cur.fetchall():
                    if first:  # get column names on the fly
                        column_names = [c[0] for c in cur.description or []]
                        first = False
                    if self._convert_row_to_dict:  # pragma: no cover
                        # strict=False: requires 3.10
                        yield dict(zip(column_names, row))
                    else:
                        yield row
            else:  # pragma: no cover
                first = True
                for row in cur.fetchall():
                    if first:  # only get description on the fly, for apsw
                        column_names = [c[0] for c in cur.description or []]
                        first = False
                    # strict=False: requires 3.10
                    yield record_class(**dict(zip(column_names, row)))
        finally:
            cur.close()

    def select_one(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:  # pragma: no cover
                column_names = [c[0] for c in cur.description or []]
                # strict=False: requires 3.10
                result = record_class(**dict(zip(column_names, result)))
            elif result is not None and self._convert_row_to_dict:  # pragma: no cover
                column_names = [c[0] for c in cur.description or []]
                result = dict(zip(column_names, result))
        finally:
            cur.close()
        return result
