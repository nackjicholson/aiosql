from collections import defaultdict

from .base import QueryLoader


class AsyncPGQueryLoader(QueryLoader):
    def __init__(self):
        self.var_replacements = defaultdict(dict)

    async def _execute_query(self, conn, op_type, sql, sql_args, return_as_dict):
        if op_type == self.op_types.SELECT:
            records = await conn.fetch(sql, *sql_args)
            if return_as_dict:
                return [dict(record) for record in records]
            else:
                return [tuple(record) for record in records]
        elif op_type == self.op_types.RETURNING:
            record = await conn.fetchrow(sql, *sql_args)
            return record[0]
        elif op_type == self.op_types.INSERT_UPDATE_DELETE:
            await conn.execute(sql, *sql_args)

    def process_sql(self, name, _op_type, sql):
        count = 0
        adj = 0

        for match in self.var_pattern.finditer(sql):
            gd = match.groupdict()
            if gd["dblquote"] is not None or gd["quote"] is not None:
                continue

            var_name = gd["var_name"]
            if var_name in self.var_replacements[name]:
                replacement = f"${self.var_replacements[name][var_name]}"
            else:
                count += 1
                replacement = f"${count}"
                self.var_replacements[name][var_name] = count

            start = match.start() + len(gd["lead"]) + adj
            end = match.end() - len(gd["trail"]) + adj

            sql = sql[:start] + replacement + sql[end:]

            replacement_len = len(replacement)
            var_len = len(var_name) + 1  # the lead : is the +1
            if replacement_len < var_len:
                adj = adj + replacement_len - var_len
            else:
                adj = adj + var_len - replacement_len

        return sql

    def create_fn(self, name, op_type, sql, return_as_dict):
        async def fn(conn, *args, **kwargs):
            if len(kwargs) > 0:
                sql_args = sorted(
                    [(self.var_replacements[name][k], v) for k, v in kwargs.items()],
                    key=lambda x: x[0],
                )
                sql_args = [a[1] for a in sql_args]
            else:
                sql_args = args

            if "acquire" in dir(conn):
                # conn is a pool
                async with conn.acquire() as con:
                    return await self._execute_query(con, op_type, sql, sql_args, return_as_dict)
            else:
                return await self._execute_query(conn, op_type, sql, sql_args, return_as_dict)

        return fn
