#####
Usage
#####

You define SQL queries in a ``greetings.sql`` file:

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select * from greetings;

    -- name: $get-users-by-username
    -- Get all the users from the database,
    -- and return them dictionaries.
    select user_id,
           username,
           name
      from users
     where username = :username;

Sync with ``sqlite3``
=====================

By specifying ``db_driver="sqlite3"`` you will use the python stdlib ``sqlite3`` driver to execute these sql queries
in python by the names you define in ``--name: foobar`` comments.

.. code-block:: python

    import sqlite3
    import aiosql

    queries = aiosql.from_path("greetings.sql", db_driver="sqlite3")
    conn = sqlite3.connect("greetings.db")

    greetings = queries.get_greetings(conn)
    users = queries.get_users_by_username(conn, username="willvaughn")
    # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
    # users = [{"user_id": 1, "username": "willvaughn", "name": "Will"}]

    name = users[0]["name"]
    for _, greeting in greetings:
       print(f"{greeting}, {name}!")

    # Hi, Will!
    # Aloha, Will!
    # Hola, Will!

    conn.close()


Going Async with ``aiosqlite``
===============================
To do this in an ``asyncio`` environment specify ``db_driver="aiosqlite"`` you can use the `aiosqlite <https://github.com/jreese/aiosqlite>`_ driver.

.. code-block:: python

    import asyncio

    import aiosql
    import aiosqlite


    async def main():
       queries = aiosql.from_path("greetings.sql", db_driver="aiosqlite")

       # Parallel queries!!!
       with async aiosqlite.connect("greetings.db") as conn:
           greetings, users = await asyncio.gather(
               queries.get_all_greetings(conn),
               queries.get_users_by_username(conn, username="willvaughn")
           )
           # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
           # users = [{"user_id": 1, "username": "willvaughn", "name": "Will"}]

       name = users[0]["name"]
       for _, greeting in greetings:
           print(f"{greeting}, {name}!")

       # Hi, Will!
       # Aloha, Will!
       # Hola, Will!


    asyncio.run(main())
