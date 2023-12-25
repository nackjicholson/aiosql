from collections import defaultdict
from contextlib import asynccontextmanager

from ..utils import VAR_REF


class MaybeAcquire:
    def __init__(self, client, driver=None):
        self.client = client
        self._driver = driver

    async def __aenter__(self):
        if "acquire" in dir(self.client):
            self._managed_conn = await self.client.acquire()
            return self._managed_conn
        else:
            self._managed_conn = None
            return self.client

    async def __aexit__(self, exc_type, exc, tb):
        if self._managed_conn is not None:
            await self.client.release(self._managed_conn)


class AsyncPGAdapter:
    is_aio_driver = True

    def __init__(self):
        self.var_sorted = defaultdict(list)

    def process_sql(self, query_name, _op_type, sql):
        adj = 0

        for match in VAR_REF.finditer(sql):
            gd = match.groupdict()
            # Do nothing if the match is found within quotes.
            if gd["dquote"] is not None or gd["squote"] is not None:
                continue

            var_name = gd["var_name"]
            if var_name in self.var_sorted[query_name]:
                replacement = f"${self.var_sorted[query_name].index(var_name) + 1}"
            else:
                replacement = f"${len(self.var_sorted[query_name]) + 1}"
                self.var_sorted[query_name].append(var_name)

            # Determine the offset of the start and end of the original
            # variable that we are replacing, taking into account an adjustment
            # factor based on previous replacements (see the note below).
            start = match.start() + len(gd["lead"]) + adj
            end = match.end() + adj

            sql = sql[:start] + replacement + sql[end:]

            # If the replacement and original variable were different lengths,
            # then the offsets of subsequent matches will be wrong by the
            # difference.  Calculate an adjustment to apply to reconcile those
            # offsets with the modified string.
            #
            # The "- 1" is to account for the leading ":" character in the
            # original string.
            adj += len(replacement) - len(var_name) - 1

        return sql

    def maybe_order_params(self, query_name, parameters):
        if isinstance(parameters, dict):
            return [parameters[rk] for rk in self.var_sorted[query_name]]
        elif isinstance(parameters, tuple):
            return parameters
        else:
            raise ValueError(f"Parameters expected to be dict or tuple, received {parameters}")

    async def select(self, conn, query_name, sql, parameters, record_class=None):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            results = await connection.fetch(sql, *parameters)
            if record_class is not None:
                results = [record_class(**dict(rec)) for rec in results]
        return results

    async def select_one(self, conn, query_name, sql, parameters, record_class=None):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            result = await connection.fetchrow(sql, *parameters)
            if result is not None and record_class is not None:
                result = record_class(**dict(result))
        return result

    async def select_value(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            return await connection.fetchval(sql, *parameters)

    @asynccontextmanager
    async def select_cursor(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            stmt = await connection.prepare(sql)
            async with connection.transaction():
                yield stmt.cursor(*parameters)

    async def insert_returning(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            res = await connection.fetchrow(sql, *parameters)
            if res:
                return res[0] if len(res) == 1 else res
            else:
                return None

    async def insert_update_delete(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            # TODO extract integer last result
            return await connection.execute(sql, *parameters)

    async def insert_update_delete_many(self, conn, query_name, sql, parameters):
        parameters = [self.maybe_order_params(query_name, params) for params in parameters]
        async with MaybeAcquire(conn) as connection:
            return await connection.executemany(sql, parameters)

    async def execute_script(self, conn, sql):
        async with MaybeAcquire(conn) as connection:
            return await connection.execute(sql)
