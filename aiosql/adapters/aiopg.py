from .apyformat import AsyncPyFormatAdapter


class AioPgAdapter(AsyncPyFormatAdapter):
    """Adapter for AioPG, which needs a cursor."""

    async def _cursor(self, conn):
        return await conn.cursor()

    async def _execute(self, conn, sql, parameters = None):
        cur = await conn.cursor()
        await cur.execute(sql, parameters)
        return cur

    async def _close(self, cur):
        cur.close()

    # AioPG does not have "executemany"
    async def insert_update_delete_many(self, conn, query_name, sql, parameters):
        cur = await self._cursor(conn)
        for params in parameters:
            await cur.execute(sql, params)
        await self._close(cur)
