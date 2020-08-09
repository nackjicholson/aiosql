# Database Driver Adapters

Database driver adapters in aiosql allow extension of the library to support additional database drivers. If you are using a driver other than the ones currently supported by built-in driver adapters (`sqlite3`, `aiosqlite`, `psycopg2`, `asyncpg`) then you will need to make your own. A database driver adapter is a duck-typed class with the following interface.

```python
class DriverAdapter:
    def process_sql(self, name, op_type, sql):
        ...

    def select(self, conn, sql, parameters, row_class=None):
        ...

    def select_one(self, conn, sql, parameters, row_class=None):
        ...

    @contextmanager
    def select_cursor(self, conn, sql, parameters):
        ...

    def insert_update_delete(self, conn, sql, parameters):
        ...

    def insert_update_delete_many(self, conn, sql, parameters):
        ...

    def insert_returning(self, conn, sql, parameters):
        ...

    def execute_script(self, conn, sql):
        ...
```

Looking at the source of the builtin [adapters/](https://github.com/nackjicholson/aiosql/tree/master/aiosql/adapters) is a great place to start seeing how you may write your own database driver adapter.

To use the adapter pass it's constructor or factory as the driver_adapter argument when building Queries.

```python
queries = aiosql.from_path("foo.sql", driver_adapter=MyDbAdapter)
```
