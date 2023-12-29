from .generic import GenericAdapter
from ..utils import VAR_REF
from .duckdb import _colon_to_dollar
from .pyformat import _replacer

from collections import defaultdict


def _colon_word_to_dollar(match):
    """Convert 'WHERE :id = 1' to 'WHERE $id = 1'."""
    gd = match.groupdict()
    if gd["dquote"] is not None:
        return gd["dquote"]
    elif gd["squote"] is not None:
        return gd["squote"]
    else:
        return f'{gd["lead"]}${gd["var_name"]}'


class ADBCAdapter(GenericAdapter):
    """ADBC Adapter

    Note that this adapter borrows heavily from the asyncpg.py adapter.
    This is beacuase at the moment ADBC doesn't seem to allow named variables
    and named params but it DOES allow for positional substitution which is what
    the postgres driver does as well.

    Todo: update this driver if/when the ADBC driver changes.

    """

    def __init__(self, driver=None, cursor_as_dict: bool = False):
        super().__init__(driver=driver)
        # whether to converts the default tuple response to a dict.
        self._convert_row_to_dict = cursor_as_dict
        self.var_sorted = defaultdict(list)

    # from asyncpg.py
    def process_sql(self, query_name, _op_type, sql):
        adj = 0

        for match in VAR_REF.finditer(sql):
            gd = match.groupdict()
            # Do nothing if the match is found within quotes.
            if gd["dquote"] is not None or gd["squote"] is not None:
                continue

            var_name = gd["var_name"]
            if var_name in self.var_sorted[query_name]:
                replacement = f"${self.var_sorted[query_name].index(var_name) + 1}"
            else:
                replacement = f"${len(self.var_sorted[query_name]) + 1}"
                self.var_sorted[query_name].append(var_name)

            # Determine the offset of the start and end of the original
            # variable that we are replacing, taking into account an adjustment
            # factor based on previous replacements (see the note below).
            start = match.start() + len(gd["lead"]) + adj
            end = match.end() + adj

            sql = sql[:start] + replacement + sql[end:]

            # If the replacement and original variable were different lengths,
            # then the offsets of subsequent matches will be wrong by the
            # difference.  Calculate an adjustment to apply to reconcile those
            # offsets with the modified string.
            #
            # The "- 1" is to account for the leading ":" character in the
            # original string.
            adj += len(replacement) - len(var_name) - 1

        return sql

    def maybe_order_params(self, query_name, parameters):
        if isinstance(parameters, dict):
            return [parameters[rk] for rk in self.var_sorted[query_name]]
        elif isinstance(parameters, tuple):
            return parameters
        else:
            raise ValueError(
                f"Parameters expected to be dict or tuple, received {parameters}"
            )

    def select(self, conn, query_name, sql, parameters, record_class=None):
        parameters = self.maybe_order_params(query_name, parameters)
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            results = cur.fetchall()
            if results is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                results = [
                    record_class(**dict(zip(column_names, row))) for row in results
                ]
        finally:
            cur.close()
        return results

    def select_one(self, conn, query_name, sql, parameters, record_class=None):
        parameters = self.maybe_order_params(query_name, parameters)
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
        parameters = self.maybe_order_params(_query_name, parameters)
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            result = cur.fetchone()
        finally:
            cur.close()
        return result[0] if result else None
