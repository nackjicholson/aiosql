from collections import defaultdict

from ..patterns import var_pattern


class MaybeAcquire:
    def __init__(self, client):
        self.client = client

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
        self.var_replacements = defaultdict(dict)

    def process_sql(self, query_name, _op_type, sql):
        count = 0
        adj = 0

        for match in var_pattern.finditer(sql):
            gd = match.groupdict()
            # Do nothing if the match is found within quotes.
            if gd["dblquote"] is not None or gd["quote"] is not None:
                continue

            var_name = gd["var_name"]
            if var_name in self.var_replacements[query_name]:
                replacement = f"${self.var_replacements[query_name][var_name]}"
            else:
                count += 1
                replacement = f"${count}"
                self.var_replacements[query_name][var_name] = count

            start = match.start() + len(gd["lead"]) + adj
            end = match.end() - len(gd["trail"]) + adj

            sql = sql[:start] + replacement + sql[end:]

            replacement_len = len(replacement)
            # the lead ":" char is the reason for the +1
            var_len = len(var_name) + 1
            if replacement_len < var_len:
                adj = adj + replacement_len - var_len
            else:
                adj = adj + var_len - replacement_len

        return sql

    def maybe_order_params(self, query_name, parameters):
        if isinstance(parameters, dict):
            xs = [(self.var_replacements[query_name][k], v) for k, v in parameters.items()]
            xs = sorted(xs, key=lambda x: x[0])
            return [x[1] for x in xs]
        elif isinstance(parameters, tuple):
            return parameters
        else:
            raise ValueError(f"Parameters expected to be dict or tuple, received {parameters}")

    async def select(self, conn, query_name, sql, parameters, return_as_dict):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            records = await connection.fetch(sql, *parameters)
            if return_as_dict:
                return [dict(record) for record in records]
            else:
                return [tuple(record) for record in records]

    async def insert_returning(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            record = await connection.fetchrow(sql, *parameters)
            return tuple(record)

    async def insert_update_delete(self, conn, query_name, sql, parameters):
        parameters = self.maybe_order_params(query_name, parameters)
        async with MaybeAcquire(conn) as connection:
            await connection.execute(sql, *parameters)

    async def insert_update_delete_many(self, conn, query_name, sql, parameters):
        parameters = [self.maybe_order_params(query_name, params) for params in parameters]
        async with MaybeAcquire(conn) as connection:
            await connection.executemany(sql, parameters)
