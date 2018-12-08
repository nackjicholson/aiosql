###############################################
Extending aiosql to additional database drivers
###############################################

Driver Adapters
---------------

Database driver adapters in ``aiosql`` are a duck-typed class which follow the below interface.::

    class MyDbAdapter():
        def process_sql(self, name, op_type, sql):
            pass

        def select(self, conn, sql, parameters):
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


    aiosql.register_driver_adapter("mydb", MyDbAdapter)

If your adapter constructor takes arguments you can register a function which can build
your adapter instance::

    def adapter_factory():
        return MyDbAdapter("foo", 42)

    aiosql.register_driver_adapter("mydb", adapter_factory)

Looking at the source of the builtin
`adapters/ <https://github.com/nackjicholson/aiosql/tree/master/aiosql/adapters>`_ is a great place
to start seeing how you may write your own database driver adapter.


TODO:

- Instructions on making new driver adapters
- How to use the ``aiosql.register_driver_adapter(driver_name, driver_adapter)`` function to add support for a new ``db_driver``
