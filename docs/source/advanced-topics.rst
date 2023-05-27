Advanced Topics
===============

Leveraging Driver Specific Features
-----------------------------------

TODO

Access the ``cursor`` object
----------------------------

The cursor is a temporary object created in memory that allows you to perform
row-by-row operations on your data and use handy methods such as
``.description``, ``.fetchall()`` and ``.fetchone()``.
As long as you are running a SQL ``SELECT`` query, you can access the cursor
object by appending ``_cursor`` to the end of the queries name.

For example, say you have the following query named ``get-all-greetings`` in a ``sql`` file:

.. code:: sql

    -- greetings.sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    SELECT
        greeting_id,
        greeting
    FROM greetings;

With this query, you can get all ``greeting_id``'s and ``greeting``'s, access the cursor object,
and print the column names with the following code:

.. code:: python

    import asyncio
    import aiosql
    import aiosqlite
    from typing import List

    queries = aiosql.from_path("greetings.sql", "aiosqlite")

    async def access_cursor():
        async with aiosqlite.connect("greetings.db") as conn:
            # append _cursor after query name
            async with queries.get_all_greetings_cursor(conn) as cur:
                print([col_info[0] for col_info in cur.description])
                first_row = await cur.fetchone()
                all_data = await cur.fetchall()
                print(f"ALL DATA: {all_data}") # list of tuples
                print(f"FIRST ROW: {first_row}") # tuple of first row data


    asyncio.run(access_cursor())
    # [greeting_id, greeting]
    # ALL DATA: [(1, hi), (2, aloha), (3, hola)]
    # FIRST ROW: (1, hi)


Accessing prepared SQL as a string
----------------------------------

When you need to do something not directly supported by aiosql, this is your escape hatch.
You can still define your sql in a file and load it with aiosql, but then you may choose to use it
without calling your aiosql method.
The prepared SQL string of a method is available as an attribute of each method ``queries.<method_name>.sql``.
Here's an example of how you might use it with a unique feature of ``psycopg2`` like
`execute_values <https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values>`__.

This example adapts the example usage from psycopg2's documentation for
`execute_values <https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values>`__.

.. code:: python

    >>> import aiosql
    >>> import psycopg2
    >>> from psycopg2.extras import execute_values
    >>> sql_str = """
    ... -- name: create_schema#
    ... create table test (id int primary key, v1 int, v2 int);
    ...
    ... -- name: insert!
    ... INSERT INTO test (id, v1, v2) VALUES %s;
    ...
    ... -- name: update!
    ... UPDATE test SET v1 = data.v1 FROM (VALUES %s) AS data (id, v1)
    ... WHERE test.id = data.id;
    ...
    ... -- name: getem
    ... select * from test order by id;
    ... """
    >>>
    >>> queries = aiosql.from_str(sql_str, "psycopg2")
    >>> conn = psycopg2.connect("dbname=test user=postgres")
    >>> queries.create_schema(conn)
    >>>
    >>> cur = conn.cursor()
    >>> execute_values(cur, queries.insert.sql, [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
    >>> execute_values(cur, queries.update.sql, [(1, 20), (4, 50)])
    >>>
    >>> queries.getem(conn)
    [(1, 20, 3), (4, 50, 6), (7, 8, 9)]

Accessing the SQL Operation Type
--------------------------------

Query functions also provide access to the SQL Operation Type you define in your library.

This can be useful for observability (such as metrics, tracing, or logging), or customizing how you
manage different operations within your codebase. Extending from the above example:

.. code:: python

    >>> import logging
    >>> import contextlib
    >>> 
    >>> reporter = logging.getLogger("metrics")
    >>>
    >>> def report_metrics(op, sql, op_time):
    ...     reporter.info(f"Operation: {op.name!r}\nSQL: {sql!r} \nTime (ms): {op_time}")
    ... 
    >>>
    >>> @contextlib.contextmanager
    ... def observe_query(func):
    ...     op = func.operation
    ...     sql = func.sql
    ...     start = time.time()
    ...     yield
    ...     end = time.time()
    ...     op_time = end - start
    ...     report_metrics(op, sql, op_time)
    ...
    >>> with observe_query(queries.getem):
    ...     queries.getem(conn)
    ... 
    [(1, 20, 3), (4, 50, 6), (7, 8, 9)]

Sync & Async
------------

Below are two example of a program which can print ``"{greeting}, {world_name}!"`` from data held
in a minimal SQLite database containing greetings and worlds. They use this same SQL.

*greetings.sql*

.. code:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select greeting_id,
           greeting
      from greetings;

    -- name: get-worlds-by-name^
    -- Get the world record from the database.
    select world_id,
           world_name
      from worlds
     where world_name = :world_name;

Notice there is a usage of the ``^`` `Select One Query Operator <./defining-sql-queries.rst#select-one>`__.
Adding this to the SQL comment ``--name: get-world-by-name^`` indicates to aiosql that
``queries.get_world_by_name()`` will return a single row back.

Sync with sqlite3
~~~~~~~~~~~~~~~~~

Here we've set up our ``sqlite3`` connection.
Using the ``sqlite3.Row`` type for our records to make it easy to access values by column names
rather than as tuple indices.
The program works, it does two queries sqequentially then loops over their results to print greetings.

.. code:: python

    import sqlite3
    import aiosql

    queries = aiosql.from_path("greetings.sql", driver_adapter="sqlite3")

    conn = sqlite3.connect("greetings.db")
    conn.row_factory = sqlite3.Row

    # greetings = [
    #     <Row greeting_id=1, greeting="Hi">,
    #     <Row greeting_id=2, greeting="Aloha">,
    #     <Row greeting_id=3, greeting="Hola">
    # ]
    greetings = queries.get_all_greetings(conn)

    # world = <Row world_id=1, world_name="Earth">
    world = queries.get_worlds_by_name(conn, world_name="Earth")

    # Hi, Earth!
    # Aloha, Earth!
    # Hola, Earth!
    for greeting_row in greetings:
        print(f"{greeting_row['greeting']}, {world['world_name']}!")

    conn.close()

Asyncio with aiosqlite
~~~~~~~~~~~~~~~~~~~~~~

This program is only a little bit different.
It let's us leverage `asyncio.gather <https://docs.python.org/3/library/asyncio-task.html#asyncio.gather>`__
to make both queries for greetings and worlds in parallel!

.. code:: python

    import asyncio

    import aiosql
    import aiosqlite


    queries = aiosql.from_path("greetings.sql", driver_adapter="aiosqlite")

    async def main():
        async with aiosqlite.connect("greetings.db") as conn:
            conn.row_factory = aiosqlite.Row
            # Parallel queries!!!
            #
            # greetings = [
            #     <Row greeting_id=1, greeting="Hi">,
            #     <Row greeting_id=2, greeting="Aloha">,
            #     <Row greeting_id=3, greeting="Hola">
            # ]
            # world = <Row world_id=1, world_name="Earth">
            greeting_rows, world = await asyncio.gather(
                queries.get_all_greetings(conn),
                queries.get_worlds_by_name(conn, world_name="Earth")
            )

            # Hi, Earth!
            # Aloha, Earth!
            # Hola, Earth!
            for greeting_row in greeting_rows:
                print(f"{greeting_row['greeting']}, {world['world_name']}!")


    asyncio.run(main())

Slightly different usage with `aiosqlite <https://github.com/omnilib/aiosqlite>`__ but I hope this
has demonstrated in a small way the big power and performance possibilities with asyncronous queries
using the async driver types.
