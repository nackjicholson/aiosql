Database Driver Adapters
========================

Database driver adapters in aiosql allow extension of the library to support additional database drivers.
If you are using a driver other than the ones currently supported by built-in driver adapters
(``sqlite3``, ``apsw``, ``aiosqlite``, ``psycopg``, ``psycopg2``, ``pg8000``, ``pygresql``, ``asyncpg``,
``pymysql``, ``mysqlclient``, ``mysql-connector``, ``duckdb``) then you will need to make your own.
A database driver adapter is a duck-typed class that follows either of the ``Protocol`` types below.
These types are defined in `aiosql/types.py <https://github.com/nackjicholson/aiosql/blob/master/aiosql/types.py>`__.

**Sync Adapter**

.. code:: python

    class SyncDriverAdapterProtocol(Protocol):
        def process_sql(self, query_name: str, op_type: SQLOperationType, sql: str) -> str:
            ...

        def select(
            self,
            conn: Any,
            query_name: str,
            sql: str,
            parameters: Union[List, Dict],
            record_class=Optional[Callable],
        ) -> List:
            ...

        def select_one(
            self,
            conn: Any,
            query_name: str,
            sql: str,
            parameters: Union[List, Dict],
            record_class=Optional[Callable],
        ) -> Optional[Any]:
            ...

        def select_cursor(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> ContextManager[Any]:
            ...

        def insert_update_delete(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> int:
            ...

        def insert_update_delete_many(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> int:
            ...

        def insert_returning(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> Optional[Any]:
            ...

        def execute_script(self, conn: Any, sql: str) -> None:
            ...

**Async Adapter**

.. code:: python

    class AsyncDriverAdapterProtocol(Protocol):
        is_aio_driver = True

        def process_sql(self, query_name: str, op_type: SQLOperationType, sql: str) -> str:
            ...

        async def select(
            self,
            conn: Any,
            query_name: str,
            sql: str,
            parameters: Union[List, Dict],
            record_class=Optional[Callable],
        ) -> List:
            ...

        async def select_one(
            self,
            conn: Any,
            query_name: str,
            sql: str,
            parameters: Union[List, Dict],
            record_class=Optional[Callable],
        ) -> Optional[Any]:
            ...

        async def select_cursor(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> AsyncContextManager[Any]:
            ...

        async def insert_update_delete(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> None:
            ...

        async def insert_update_delete_many(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> None:
            ...

        async def insert_returning(
            self, conn: Any, query_name: str, sql: str, parameters: Union[List, Dict]
        ) -> Optional[Any]:
            ...

        async def execute_script(self, conn: Any, sql: str) -> None:
            ...

There isn't much difference between these two protocols besides the ``async def`` syntax for the method definition.
There is one more sneaky difference, the aiosql code expects async adapters to have a static class field
``is_aio_driver = True`` so it can tell when to use ``await`` for method returns.
Looking at the source of the builtin
`adapters/ <https://github.com/nackjicholson/aiosql/tree/master/aiosql/adapters>`__ is a great place to start
seeing how you may write your own database driver adapter.

To use the adapter pass its constructor or factory as the ``driver_adapter`` argument when building Queries:

.. code:: python

    queries = aiosql.from_path("foo.sql", driver_adapter=MyDbAdapter)

Alternatively, an adapter can be registered or overriden:

.. code:: python

    # in MyDbAdapter provider, eg module "mydb_aiosql"
    aiosql.register_adapter("mydb", MyDbAdapter)

    # then use it elsewhere
    import aiosql
    import mydb_aiosql
    queries = aiosql.from_path("some.sql", "mydb")


Please ask questions on `GitHub Issues <https://github.com/nackjicholson/aiosql/issues>`__.
If the community makes additional adapter add-ons I'll be sure to list them here.
