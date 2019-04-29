from contextlib import contextmanager

from ..patterns import var_pattern


def replacer(match):
    gd = match.groupdict()
    if gd["dblquote"] is not None:
        return gd["dblquote"]
    elif gd["quote"] is not None:
        return gd["quote"]
    else:
        return f'{gd["lead"]}%({gd["var_name"]})s{gd["trail"]}'


class PsycoPG2Adapter:
    def __init__(self, dataclass_map=None):
        self._dataclass_map = dataclass_map if dataclass_map is not None else {}

    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        return var_pattern.sub(replacer, sql)

    def select(self, conn, _query_name, sql, parameters, dataclass_name=None):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            rows = cur.fetchall()
        if dataclass_name is None:
            return rows
        else:
            cls = self._dataclass_map[dataclass_name]
            column_names = [c.name for c in cur.description]
            return [cls(**dict(zip(column_names, row))) for row in rows]

    @staticmethod
    @contextmanager
    def select_cursor(conn, _query_name, sql, parameters):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            yield cur

    @staticmethod
    def insert_update_delete(conn, _query_name, sql, parameters):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)

    @staticmethod
    def insert_update_delete_many(conn, _query_name, sql, parmeters):
        with conn.cursor() as cur:
            cur.executemany(sql, parmeters)

    @staticmethod
    def insert_returning(conn, _query_name, sql, parameters):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            res = cur.fetchone()
            if res:
                return res[0] if len(res) == 1 else res
            else:
                return None

    @staticmethod
    def execute_script(conn, sql):
        with conn.cursor() as cur:
            cur.execute(sql)
