###############################################
Extending aiosql to additional database drivers
###############################################

Driver Adapters
---------------

Database driver adapters in ``aiosql`` are a duck-typed class which follow the below interface.::

    class MyDbAdapter():
        def process_sql(self, name, op_type, sql):
            pass

        def select(self, conn, sql, parameters, row_class=None):
            pass

        def select_one(self, conn, sql, parameters, row_class=None):
            pass

        @contextmanager
        def select_cursor(self, conn, sql, parameters):
            pass


        def insert_update_delete(self, conn, sql, parameters):
            pass

        def insert_update_delete_many(self, conn, sql, parameters):
            pass

        def insert_returning(self, conn, sql, parameters):
            pass

        def execute_script(self, conn, sql):
            pass


If your adapter constructor takes arguments you can register a function which can build
your adapter instance::

    def adapter_factory():
        return MyDbAdapter("foo", 42)

Looking at the source of the builtin
`adapters/ <https://github.com/nackjicholson/aiosql/tree/master/aiosql/adapters>`_ is a great place
to start seeing how you may write your own database driver adapter.

To use the adapter pass it's constructor or factory as the driver_adapter argument when building Queries::

    queries = aiosql.from_path("foo.sql", driver_adapter=MyDbAdapter)
