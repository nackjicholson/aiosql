from contextlib import asynccontextmanager
from ..types import AsyncDriverAdapterProtocol

# it is unclear how generic is this class
class AsyncGenericAdapter(AsyncDriverAdapterProtocol):

    is_aio_driver = True

    def process_sql(self, query_name, op_type, sql):
        return sql  # pragma: no cover

    # abstractions needed for aiopg
    async def _cursor(self, conn):
        return conn.cursor()

    async def _execute(self, conn, sql, parameters = None):
        return await conn.execute(sql, parameters)

    async def _close(self, cur):
        await cur.close()

    # this is an asynchronous generator
    async def select(self, conn, query_name, sql, parameters, record_class=None):
        cur = await self._execute(conn, sql, parameters)
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
            await self._close(cur)

    async def select_one(self, conn, query_name, sql, parameters, record_class=None):
        cur = await self._execute(conn, sql, parameters)
        result = await cur.fetchone()
        if result is not None and record_class is not None:
            column_names = [c[0] for c in cur.description]
            result = record_class(**dict(zip(column_names, result)))
        await self._close(cur)
        return result

    async def select_value(self, conn, query_name, sql, parameters):
        cur = await self._execute(conn, sql, parameters)
        result = await cur.fetchone()
        res = result[0] if result else None
        await self._close(cur)
        return res

    @asynccontextmanager
    async def select_cursor(self, conn, query_name, sql, parameters):
        cur = await self._execute(conn, sql, parameters)
        yield cur
        await self._close(cur)

    async def insert_returning(self, conn, query_name, sql, parameters):
        cur = await self._execute(conn, sql, parameters)
        result = await cur.fetchone()
        # res = result[0] if result else None
        await self._close(cur)
        return result

    async def insert_update_delete(self, conn, query_name, sql, parameters):
        cur = await self._execute(conn, sql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else None
        await self._close(cur)
        return rc

    async def insert_update_delete_many(self, conn, query_name, sql, parameters):
        cur = await self._cursor(conn)
        res = await cur.executemany(sql, parameters)
        await self._close(cur)
        return res

    async def execute_script(self, conn, sql):
        cur = await self._execute(conn, sql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        await self._close(cur)
        return msg
