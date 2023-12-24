from contextlib import asynccontextmanager


class AioSQLiteAdapter:
    is_aio_driver = True

    def process_sql(self, _query_name, _op_type, sql):
        """Pass through function because the ``aiosqlite`` driver can already handle the
        ``:var_name`` format used by aiosql and doesn't need any additional processing.

        Args:

        - _query_name (str): The name of the sql query.
        - _op_type (SQLOperationType): The type of SQL operation performed by the query.
        - sql (str): The sql as written before processing.

        Returns:

        - str: Original SQL text unchanged.
        """
        return sql

    async def select(self, conn, _query_name, sql, parameters, record_class=None):
        async with conn.execute(sql, parameters) as cur:
            results = await cur.fetchall()
            if record_class is not None:
                column_names = [c[0] for c in cur.description]
                results = [record_class(**dict(zip(column_names, row))) for row in results]
        return results

    async def select_one(self, conn, _query_name, sql, parameters, record_class=None):
        async with conn.execute(sql, parameters) as cur:
            result = await cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                result = record_class(**dict(zip(column_names, result)))
        return result

    async def select_value(self, conn, _query_name, sql, parameters):
        async with conn.execute(sql, parameters) as cur:
            result = await cur.fetchone()
        return result[0] if result else None

    @asynccontextmanager
    async def select_cursor(self, conn, _query_name, sql, parameters):
        async with conn.execute(sql, parameters) as cur:
            yield cur

    async def insert_returning(self, conn, _query_name, sql, parameters):
        async with conn.execute(sql, parameters) as cur:
            return cur.lastrowid

    async def insert_update_delete(self, conn, _query_name, sql, parameters):
        async with conn.execute(sql, parameters) as cur:
            return cur.rowcount

    async def insert_update_delete_many(self, conn, _query_name, sql, parameters):
        cur = await conn.executemany(sql, parameters)
        await cur.close()

    async def execute_script(self, conn, sql):
        await conn.executescript(sql)
        return "DONE"
