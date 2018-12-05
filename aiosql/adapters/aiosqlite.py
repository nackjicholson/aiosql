class AioSQLiteAdapter:
    is_aio_driver = True

    @staticmethod
    def process_sql(_query_name, _op_type, sql):
        """Pass through function because the ``aiosqlite`` driver can already handle the
        :var_name format used by aiosql and doesn't need any additional processing.

        Args:
            _query_name (str): The name of the sql query.
            _op_type (SQLOperationType): The type of SQL operation performed by the query.
            sql (str): The sql as written before processing.

        Returns:
            str: Original SQL text unchanged.
        """
        return sql

    @staticmethod
    async def select(conn, _query_name, sql, parameters, return_as_dict):
        async with conn.execute(sql, parameters) as cur:
            rows = await cur.fetchall()

            if return_as_dict:
                cols = [col[0] for col in cur.description]
                rows = [dict(zip(cols, row)) for row in rows]

            return rows

    @staticmethod
    async def insert_returning(conn, _query_name, sql, parameters):
        async with conn.execute(sql, parameters) as cur:
            return cur.lastrowid

    @staticmethod
    async def insert_update_delete(conn, _query_name, sql, parameters):
        cur = await conn.execute(sql, parameters)
        await cur.close()

    @staticmethod
    async def insert_update_delete_many(conn, _query_name, sql, parameters):
        cur = await conn.executemany(sql, parameters)
        await cur.close()
