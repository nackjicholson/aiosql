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
    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        return var_pattern.sub(replacer, sql)

    @staticmethod
    def select(conn, _query_name, sql, parameters, row_class=None):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            rows = cur.fetchall()
        if row_class is None:
            return rows
        else:
            # cls = self._dataclass_map[row_class]
            column_names = [c.name for c in cur.description]
            return [row_class(**dict(zip(column_names, row))) for row in rows]

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
