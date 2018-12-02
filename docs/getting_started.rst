###############
Getting Started
###############

Below is an example of a program which can pring "{greeting}, {world_name}!" from data held in a minimal SQLite database of
worlds and greetings.

The SQL is in a ``greetings.sql`` file with ``-- name: `` definitions on each query to tell ``aiosql`` under which name
we would like to be able to execute this code. The name ``get-all-greetings`` will be available to us after loading as
a method ``get_all_greetings(conn)``. Each method on an ``aiosql.Queries`` object accepts a database connection it can
use in order to communicate with a database.

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select * from greetings;

    -- name: $get-worlds-by-name
    -- Get all the world record from the database.
    select world_id,
           world_name,
           location
      from worlds
     where world_name = :world_name;

By specifying ``db_driver="sqlite3"`` we can use the python stdlib ``sqlite3`` driver to execute these sql queries and
get the results.

.. code-block:: python

    import sqlite3
    import aiosql

    queries = aiosql.from_path("greetings.sql", db_driver="sqlite3")
    conn = sqlite3.connect("greetings.db")

    greetings = queries.get_greetings(conn)
    worlds = queries.get_worlds_by_name(conn, world_name="Earth")
    # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
    # worlds = [{"world_id": 1, "world_name": "Earth"}]

    for world in worlds:
        for _, greeting in greetings:
            print(f"{greeting}, {world['world_name']}!")

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
            # Parallel queries!!!
            greetings, worlds = await asyncio.gather(
                queries.get_all_greetings(conn),
                queries.get_worlds_by_name(conn, world_name="Earth")
            )
            # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
            # worlds = [{"world_id": 1, "world_name": "Earth"}]

            for world in worlds:
                for _, greeting in greetings:
                    print(f"{greeting}, {world['world_name']}!")

            # Hi, Earth!
            # Aloha, Earth!
            # Hola, Earth!


    asyncio.run(main())
