###############
Getting Started
###############

Below is an example of a program which can print ``"{greeting}, {world_name}!"`` from data held in a minimal SQLite
database containing greetings and worlds.

The SQL is in a ``greetings.sql`` file with ``-- name:`` definitions on each query to tell ``aiosql`` under which name
we would like to be able to execute them. For example, the query under the name ``get-all-greetings`` in the example
below will be available to us after loading via ``aiosql.from_path`` as a method ``get_all_greetings(conn)``.
Each method on an ``aiosql.Queries`` object accepts a database connection to use in communicating with the database.

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select greeting_id, greeting from greetings;

    -- name: get-worlds-by-name
    -- Get all the world record from the database.
    select world_id,
           world_name,
           location
      from worlds
     where world_name = :world_name;

By specifying ``db_driver="sqlite3"`` we can use the python stdlib ``sqlite3`` driver to execute these sql queries and
get the results. We're also using the ``sqlite3.Row`` type for our records to make it easy to access our data via
their column names rather than as tuple indices.

.. code-block:: python

    import sqlite3
    import aiosql

    queries = aiosql.from_path("greetings.sql", db_driver="sqlite3")
    conn = sqlite3.connect("greetings.db")
    conn.row_factory = sqlite3.Row

    greetings = queries.get_greetings(conn)
    worlds = queries.get_worlds_by_name(conn, world_name="Earth")
    # greetings = [
    #     <Row greeting_id=1, greeting="Hi">,
    #     <Row greeting_id=2, greeting="Aloha">,
    #     <Row greeting_id=3, greeting="Hola">
    # ]
    # worlds = [<Row world_id=1, world_name="Earth">]

    for world_row in worlds:
        for greeting_row in greetings:
            print(f"{greeting_row['greeting']}, {world_row['world_name']}!")
    # Hi, Earth!
    # Aloha, Earth!
    # Hola, Earth!

    conn.close()


We can also use our ``greetings.db`` SQLite database with the `aiosqlite <https://github.com/jreese/aiosqlite>`_ driver
with ``db_driver="aiosqlite"``. It's a little bit different, but lets us leverage ``asyncio.gather`` to make
both our queries for greetings and worlds in parallel!

.. code-block:: python

    import asyncio

    import aiosql
    import aiosqlite

    queries = aiosql.from_path("greetings.sql", db_driver="aiosqlite")


    async def main():
        with async aiosqlite.connect("greetings.db") as conn:
            conn.row_factory = aiosqlite.Row
            # Parallel queries!!!
            greetings, worlds = await asyncio.gather(
                queries.get_all_greetings(conn),
                queries.get_worlds_by_name(conn, world_name="Earth")
            )
            # greetings = [
            #     <Row greeting_id=1, greeting="Hi">,
            #     <Row greeting_id=2, greeting="Aloha">,
            #     <Row greeting_id=3, greeting="Hola">
            # ]
            # worlds = [<Row world_id=1, world_name="Earth">]

            for world_row in worlds:
                for greeting_row in greetings:
                    print(f"{greeting_row['greeting']}, {world_row['world_name']}!")
            # Hi, Earth!
            # Aloha, Earth!
            # Hola, Earth!


    asyncio.run(main())
