Database Driver Adapters
========================

Database driver adapters in aiosql allow extension of the library to support
additional database drivers.
If you are using a driver other than the ones currently supported by built-in
driver adapters (``sqlite3``, ``apsw``, ``aiosqlite``, ``psycopg``,
``psycopg2``, ``pg8000``, ``pygresql``, ``asyncpg``, ``pymysql``,
``mysqlclient``, ``mysql-connector``, ``duckdb``, ``pymssql``),
first check whether your driver supports *pyformat* or *named* paramstyles.
If so, check (manually) whether the default PEP 249 drivers work:

.. code:: python

    import acmedb  # your PEP 249 driver
    import aiosql

    conn = acmedb.connect("…")
    queries = aiosql.from_str("-- name: add42$\nSELECT :n + 42;\n", acmedb)
    assert queries.add42(conn, n=18) == 60

If this simplistic test works, do more tests involving all operators (see the
pytest tests), then create an issue to notify that your driver works out of the
box so it can be advertised from the readme.

If it does not work or if you have an asynchronous driver, you will need to make
your own.
Good news, it should be very close to the existing supported drivers.
A database driver adapter is a duck-typed class that follows either of the
``Protocol`` types defined in
`aiosql/types.py <https://github.com/nackjicholson/aiosql/blob/main/aiosql/types.py>`__:

.. literalinclude:: ../../aiosql/types.py
   :language: python
   :lines: 61-104
   :caption: PEP 249 Synchronous Adapter

.. literalinclude:: ../../aiosql/types.py
   :language: python
   :lines: 107-152
   :caption: Asynchronous Adapter

Some comments about these classes, one for synchronous queries (PEP 249) and
the other for asynchronous queries:

- ``_cursor`` is an internal method to generate a cursor, as some drivers
  need to pass parameters at this phase.
- ``process_sql`` is used to preprocess SQL queries so has to handle named
  parameters as they are managed by the target driver.
- ``select``, ``select_one``, ``insert_update_delete``, ``insert_update_delete_many``,
  ``insert_returning`` and ``execute_script`` implement all operations.
- ``select_cursor`` returns the raw cursor from a ``select``.

There isn't much difference between these two protocols besides the
``async def`` syntax for the method definition.
There is one more sneaky difference, the aiosql code expects async adapters to
have a static class field ``is_aio_driver = True`` so it can tell when to use
``await`` for method returns.
Looking at the source of the builtin
`adapters/ <https://github.com/nackjicholson/aiosql/tree/main/aiosql/adapters>`__
is a great place to start seeing how you may write your own database driver adapter.

For a PEP 249 driver, consider inheriting from ``aiosql.adapters.Generic`` if you can.

To use the adapter pass its constructor or factory as the ``driver_adapter``
argument when building Queries:

.. code:: python

    queries = aiosql.from_path("foo.sql", driver_adapter=AcmeAdapter)

Alternatively, an adapter can be registered or overriden:

.. code:: python

    # in AcmeAdapter provider, eg module "acmedb_aiosql"
    import aiosql
    aiosql.register_adapter("acmedb", AcmeAdapter)

    # then use it elsewhere
    import aiosql
    queries = aiosql.from_path("some.sql", "acmedb")

Please ask questions on `GitHub Issues <https://github.com/nackjicholson/aiosql/issues>`__.
If the community makes additional adapter add-ons it will be listed from the doc.
