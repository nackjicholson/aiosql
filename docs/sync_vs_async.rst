#############
Sync vs Async
#############

sqlite3
=======

Below is an example of a program which can print ``"{greeting}, {world_name}!"`` from data held in a minimal SQLite
database containing greetings and worlds.

The SQL is in a ``greetings.sql`` file with ``-- name:`` definitions on each query to tell ``aiosql`` under which name
we would like to be able to execute them from our Python application.

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select greeting_id, greeting from greetings;

    -- name: get-worlds-by-name
    -- Get the world record from the database.
    select world_id,
           world_name
      from worlds
     where world_name = :world_name;

To load these queries into python we can use ``aiosql.from_path``.

.. code-block:: python

    import sqlite3
    import aiosql

    queries = aiosql.from_path("greetings.sql", driver_adapter="sqlite3")

The query under the name ``get-all-greetings`` will now be available as a method ``queries.get_all_greetings()``
and ``get-worlds-by-name`` will be available as ``queries.get_worlds_by_name()``

By specifying ``driver_adapter="sqlite3"`` we are letting ``aiosql`` know that to execute the queries it
will be receiving a ``sqlite3`` connection as the first argument of each method.
It's worth repeating, each method on an ``aiosql.Queries`` object accepts a database connection to use in
communicating with the database, all of it's other variables used for substitution in the SQL are passed as
additional keyword arguments.

.. code-block:: python

    conn = sqlite3.connect("greetings.db")
    conn.row_factory = sqlite3.Row

    # greetings = [
    #     <Row greeting_id=1, greeting="Hi">,
    #     <Row greeting_id=2, greeting="Aloha">,
    #     <Row greeting_id=3, greeting="Hola">
    # ]
    greetings = queries.get_greetings(conn)

    # worlds = [<Row world_id=1, world_name="Earth">]
    worlds = queries.get_worlds_by_name(conn, world_name="Earth")

    # Hi, Earth!
    # Aloha, Earth!
    # Hola, Earth!
    for world_row in worlds:
        for greeting_row in greetings:
            print(f"{greeting_row['greeting']}, {world_row['world_name']}!")

    conn.close()

Here we've set up our ``sqlite3`` connection. Using the ``sqlite3.Row`` type for our records to make it easy to access our
data via their column names rather than as tuple indices. This is a nice feature of ``sqlite3`` and ``aiosql`` doesn't
ruin it for us.

aiosqlite
=========

We can also use our ``greetings.db`` SQLite database with the `aiosqlite <https://github.com/jreese/aiosqlite>`_ driver
by specifying ``driver_adapter="aiosqlite"``. It's a little bit different, but lets us leverage ``asyncio.gather`` to make
both our queries for greetings and worlds in parallel! I'll throw in a few changes that demonstrate some other
cool features of ``aiosql`` as well.

1. ``record_class`` directive.
    - Enables marshalling rows out of SQL into python domain objects like `@dataclass` instances or `NamedTuple`.
      In this example it is used to build instances of ``World`` and ``Greeting``.
2. ``^`` Select One Query Operator
    - Adding this to the SQL comment ``--name: get-world-by-name^`` indicates to ``aiosql`` that when we call the
      ``queries.get_world_by_name()`` method we should get a single row back.

.. code-block:: sql

    -- name: get-all-greetings
    -- record_class: Greeting
    -- Get all the greetings in the database
    select greeting_id, greeting from greetings;

    -- name: get-world-by-name^
    -- record_class: World
    -- Get the world record from the database.
    select world_id,
           world_name
      from worlds
     where world_name = :world_name;

.. code-block:: python

    import asyncio

    import aiosql
    import aiosqlite
    from typing import NamedTuple


    class Greeting(NamedTuple):
        greeting_id: int
        greeting: str


    class World(NamedTuple)
        world_id: int,
        world_name: str


    queries = aiosql.from_path(
        "greetings.sql",
        driver_adapter="aiosqlite",
        record_classes={"Greeting": Greeting, "World": World}
    )

    async def main():
        with async aiosqlite.connect("greetings.db") as conn:
            # Parallel queries!!!
            #
            # greetings = [
            #     <Greeting greeting_id=1, greeting="Hi">,
            #     <Greeting greeting_id=2, greeting="Aloha">,
            #     <Greeting greeting_id=3, greeting="Hola">
            # ]
            # world = <World world_id=1, world_name="Earth">
            greetings, world = await asyncio.gather(
                queries.get_all_greetings(conn),
                queries.get_world_by_name(conn, world_name="Earth")
            )

            # Hi, Earth!
            # Aloha, Earth!
            # Hola, Earth!
            for greeting in greetings:
                print(f"{greeting_row.greeting}, {world.world_name}!")


    asyncio.run(main())
