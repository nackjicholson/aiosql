from contextlib import asynccontextmanager
from ..types import AsyncDriverAdapterProtocol

# it is unclear how generic is this class
class AsyncGenericAdapter(AsyncDriverAdapterProtocol):

    is_aio_driver = True

    def process_sql(self, query_name, op_type, sql):
        return sql  # pragma: no cover

    # this is an asynchronous generator
    async def select(self, conn, query_name, sql, parameters, record_class=None):
        cur = await conn.execute(sql, parameters)
        try:
            if record_class is not None:
                column_names = [c[0] for c in cur.description]
                for row in await cur.fetchall():
                    yield record_class(**dict(zip(column_names, row)))
            else:
                # psycopg 3.3: async for row in cur.results():
                for row in await cur.fetchall():
                    yield row
        finally:
            await cur.close()

    async def select_one(self, conn, query_name, sql, parameters, record_class=None):
        cur = await conn.execute(sql, parameters)
        result = await cur.fetchone()
        if result is not None and record_class is not None:
            column_names = [c[0] for c in cur.description]
            result = record_class(**dict(zip(column_names, result)))
        await cur.close()
        return result

    async def select_value(self, conn, query_name, sql, parameters):
        cur = await conn.execute(sql, parameters)
        result = await cur.fetchone()
        res = result[0] if result else None
        await cur.close()
        return res

    @asynccontextmanager
    async def select_cursor(self, conn, query_name, sql, parameters):
        cur = await conn.execute(sql, parameters)
        yield cur
        await cur.close()

    async def insert_returning(self, conn, query_name, sql, parameters):
        cur = await conn.execute(sql, parameters)
        result = await cur.fetchone()
        # res = result[0] if result else None
        await cur.close()
        return result

    async def insert_update_delete(self, conn, query_name, sql, parameters):
        cur = await conn.execute(sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else None
        await cur.close()
        return rc

    async def insert_update_delete_many(self, conn, query_name, sql, parameters):
        cur = conn.cursor()
        res = await cur.executemany(sql, parameters)
        await cur.close()
        return res

    async def execute_script(self, conn, sql):
        cur = await conn.execute(sql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        await cur.close()
        return msg
