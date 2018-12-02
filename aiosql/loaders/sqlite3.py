from .base import QueryLoader, SQLOperationType


class SQLite3QueryLoader(QueryLoader):
    def process_sql(self, _name, _op_type, sql):
        """Pass through function because the ``sqlite3`` driver can already handle the
        ``:var_name`` format used by aiosql and so doesn't need any additional processing.

        Args:
            _name (str): The name of the sql query.
            _op_type (SQLOperationType): The type of SQL operation performed by the query.
            sql (str): The sql as written before processing.

        Returns:
            str: Original SQL text unchanged.
        """
        return sql

    def create_fn(self, name, op_type, sql, return_as_dict):
        """Creates function which can determine how to execute a SQLite query.

        Leverages the ``self.op_types`` enum to determine which operation type needs to be performed
        and expects to be passed a ``sqlite3`` connection object to work with.

        Args:
            name (str): The name of the sql query.
            op_type (SQLOperationType): The type of SQL operation performed by the query.
            sql (str): The processed SQL to be executed.
            return_as_dict (bool): Whether or not to return rows as dictionaries using column names.

        Returns:
            callable: Function which executes SQLite query and return results.
        """

        def fn(conn, *args, **kwargs):
            results = None
            cur = conn.cursor()
            cur.execute(sql, kwargs if len(kwargs) > 0 else args)

            if op_type == self.op_types.SELECT:
                if return_as_dict:
                    cols = [col[0] for col in cur.description]
                    results = [dict(zip(cols, row)) for row in cur.fetchall()]
                else:
                    results = cur.fetchall()
            elif op_type == self.op_types.RETURNING:
                results = cur.lastrowid

            cur.close()

            return results

        return fn
