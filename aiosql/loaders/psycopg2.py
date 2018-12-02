from .base import QueryLoader, SQLOperationType


def replacer(match):
    gd = match.groupdict()
    if gd["dblquote"] is not None:
        return gd["dblquote"]
    elif gd["quote"] is not None:
        return gd["quote"]
    else:
        return f'{gd["lead"]}%({gd["var_name"]})s{gd["trail"]}'


class PsycoPG2QueryLoader(QueryLoader):
    def process_sql(self, _name, _op_type, sql):
        """Replaces aiosql style variables ``:var_name`` with psycopg2 variable replacement syntax
        of ``%(var_name)s``.

        Args:
            _name (str): The name of the sql query.
            _op_type (SQLOperationType): The type of SQL operation performed by
                                                             the query.
            sql (str): The sql as written before processing.

        Returns:

        """
        return self.var_pattern.sub(replacer, sql)

    def create_fn(self, _name, op_type, sql, return_as_dict):
        """Create function which can determine how to execute a PostgreSQL query.

        Args:
            _name (str): The name of the sql query.
            op_type (SQLOperationType): The type of SQL operation performed by
            sql (str): SQL text prepared for use by ``psycopg2`` driver.
            return_as_dict (bool): Whether or not to return rows as dictionaries using column names.

        Returns:
            callable: Function which executes PostgreSQL query and return results.
        """

        def fn(conn, *args, **kwargs):
            with conn.cursor() as cur:
                cur.execute(sql, kwargs if len(kwargs) > 0 else args)
                if op_type == self.op_types.INSERT_UPDATE_DELETE:
                    return None
                elif op_type == self.op_types.SELECT:
                    if return_as_dict:
                        cols = [col[0] for col in cur.description]
                        return [dict(zip(cols, row)) for row in cur.fetchall()]
                    else:
                        return cur.fetchall()
                elif op_type == self.op_types.RETURNING:
                    pool = cur.fetchone()
                    return pool[0] if pool else None
                else:
                    raise RuntimeError(f"Unknown SQLOperationType: {op_type}")

        return fn
