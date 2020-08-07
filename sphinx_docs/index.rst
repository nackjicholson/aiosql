.. aiosql documentation master file, created by
   sphinx-quickstart on Thu Nov 29 11:57:02 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#############################
aiosql - Simple SQL in Python
#############################

SQL is code, you should be able to write it, version control it, comment on it, and use it in database tools
like ``psql`` as you would any other SQL. But, you also want to be able to use it from your python
applications, and that's where ``aiosql`` can help. With ``aiosql`` you can organize your SQL statements in ``.sql``
files and load them into a python object as methods to call.

This project supports standard and ``asyncio`` based drivers for SQLite (``sqlite3``, ``aiosqlite``) and PostgreSQL
(``psycopg2``, ``asyncpg``) out of the box, and can be extended to support other database drivers by you!
``asyncio`` support restricts this package to python versions >3.6. If you are using older versions of python
please see the related `anosql <https://github.com/honza/anosql>`_ package which this project is based on.

Contents
========

.. toctree::
   :maxdepth: 2

   Install <install>
   Getting Started <getting_started>
   Sync vs Async <sync_vs_async>
   Defining Queries <defining_queries>
   Extending aiosql <driver_adapters>
   Upgrading <upgrading>
   API <source/modules>

Quick Example
=============

*greetings.sql*

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select greeting_id, greeting from greetings;

    -- name: get-user-by-username^
    -- record_class: User
    -- Get all the users from the database,
    -- and return it as a dict
    select user_id,
           username,
           name
      from users
     where username = :username;

*example.py*

.. code-block:: python

    import asyncio
    import aiosql
    import aiosqlite
    from dataclasses import dataclass


    @dataclass
    class User:
        user_id: int
        username: str
        name: str


    queries = aiosql.from_path(
        "greetings.sql",
        "aiosqlite",
        record_classes={"User": User}
    )


    async def main():
       # Parallel queries!!!
       async with aiosqlite.connect("greetings.db") as conn:
           greetings, user = await asyncio.gather(
               queries.get_all_greetings(conn),
               queries.get_user_by_username(conn, username="willvaughn")
           )
           # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
           # user = User(1, "willvaughn", "Will")

           for _, greeting in greetings:
               print(f"{greeting}, {user.name}!)


    asyncio.run(main())

##################
Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
