from contextlib import contextmanager


def _record_generator(cur, sql, parameters, record_class):
    """Generate records for each row returned by the query. This function is necessary because the
    cursor description is only available during query execution and not afterwards. The description
    is cached inside APSW, so it is cheap to call getdescription repeatedly.
    """
    yield from (
        record_class(**dict(zip((c[0] for c in cur.getdescription()), row)))
        for row in cur.execute(sql, parameters)
    )


class APSWDriverAdapter:
    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        """Pass through function because the ``apsw`` driver already handles the :var_name
        "named style" syntax used by aiosql variables. Note, it will also accept "qmark style"
        variables.

        Args:
            _query_name (str): The name of the sql query. Unused.
            _op_type (aiosql.SQLOperationType): The type of SQL operation performed by the sql.
            sql (str): The sql as written before processing.

        Returns:
            str: Original SQL text unchanged.
        """
        return sql

    @staticmethod
    def select(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        if record_class is not None:
            results = _record_generator(cur, sql, parameters, record_class)
        else:
            results = cur.execute(sql, parameters)
        return list(results)

    @staticmethod
    def select_one(conn, _query_name, sql, parameters, record_class=None):
        cur = conn.cursor()
        if record_class is not None:
            return next(_record_generator(cur, sql, parameters, record_class), None,)
        cur.execute(sql, parameters)
        return cur.fetchone()

    @staticmethod
    @contextmanager
    def select_cursor(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        cur.execute(sql, parameters)
        yield cur

    @staticmethod
    def insert_update_delete(conn, _query_name, sql, parameters):
        conn.cursor().execute(sql, parameters)

    @staticmethod
    def insert_update_delete_many(conn, _query_name, sql, parameters):
        conn.cursor().executemany(sql, parameters)

    @staticmethod
    def insert_returning(conn, _query_name, sql, parameters):
        conn.cursor().execute(sql, parameters)
        return conn.last_insert_rowid()

    @staticmethod
    def execute_script(conn, sql):
        conn.cursor().execute(sql)
