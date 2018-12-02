from .base import QueryLoader


class AioSQLiteQueryLoader(QueryLoader):
    def process_sql(self, _name, _op_type, sql):
        """Pass through function because the ``aiosqlite`` driver can already handle the
        ``:var_name`` format used by aiosql and so doesn't need any additional processing.

        Args:
            _name (str): The name of the sql query.
            _op_type (SQLOperationType): The type of SQL operation performed by
                                                             the query.
            sql (str): The sql as written before processing.

        Returns:
            str: Original SQL text unchanged.
        """
        return sql

    def create_fn(self, _name, op_type, sql, return_as_dict):
        """Creates async coroutine function which can determine how to execute a SQLite query.

        Leverages the ``self.op_types`` enum to determine which operation type needs to be performed
        and expects to be passed a ``aiosqlite`` connection object to work with.

        Args:
            _name (str): The name of the sql query.
            _op_type (SQLOperationType): The type of SQL operation performed by the query.
            sql (str): The processed SQL to be executed.
            return_as_dict (bool): Whether or not to return rows as dictionaries using column names.

        Returns:
            callable: Asynchronous coroutine which executes SQLite query and return results.
        """

        async def fn(conn, *args, **kwargs):
            results = None
            cur = await conn.execute(sql, kwargs if len(kwargs) > 0 else args)

            if op_type == self.op_types.SELECT:
                if return_as_dict:
                    cols = [col[0] for col in cur.description]
                    results = []
                    async for row in cur:
                        results.append(dict(zip(cols, row)))
                else:
                    results = await cur.fetchall()
            elif op_type == self.op_types.RETURNING:
                results = cur.lastrowid

            await cur.close()

            return results

        return fn
