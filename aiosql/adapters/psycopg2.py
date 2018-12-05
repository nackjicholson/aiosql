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
    is_aio_driver = False

    @staticmethod
    def process_sql(_name, _op_type, sql):
        return var_pattern.sub(replacer, sql)

    @staticmethod
    def select(conn, _name, sql, parameters, return_as_dict):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            rows = cur.fetchall()

            if return_as_dict:
                cols = [col[0] for col in cur.description]
                rows = [dict(zip(cols, row)) for row in rows]

            return rows

    @staticmethod
    def insert_update_delete(conn, _name, sql, parameters):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)

    @staticmethod
    def insert_update_delete_many(conn, _name, sql, parmeters):
        with conn.cursor() as cur:
            cur.executemany(sql, parmeters)

    @staticmethod
    def insert_returning(conn, _name, sql, parameters):
        with conn.cursor() as cur:
            cur.execute(sql, parameters)
            res = cur.fetchone()
            return res if res else None
