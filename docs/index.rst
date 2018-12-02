.. aiosql documentation master file, created by
   sphinx-quickstart on Thu Nov 29 11:57:02 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#############################
aiosql - Simple SQL in Python
#############################

SQL is code, you should be able to write it, version control it, comment on it, and use it in database tools
like ``psql`` as you would any other SQL. But, you also want to be able to use it from your python
applications, and that's where ``aiosql`` can help. With ``aiosql`` you can organize your SQL in ``.sql``
files and load them into a python object with methods to call.

The project is based on (and closely related to) the python package `anosql <https://github.com/honza/anosql>`_, which
is based on the clojure library `Yesql <https://github.com/krisajenkins/yesql/>`_. It supports sync and asyncio
drivers for SQLite and PostgreSQL out of the box, and can be extended by you to support other database drivers!

#######
Install
#######

.. code-block:: shell

    pip install aiosql

Or if you you use `poetry <https://poetry.eustace.io/>`_:

.. code-block:: shell

   poetry add aiosql


#####
Usage
#####

Basics
======

You define SQL queries in a ``greetings.sql`` file:

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select * from greetings;

    -- name: $get-users-by-username
    -- Get all the users from the database,
    -- and return it as a dict
    select * from users where username = :username;

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

#################
API Documentation
#################

.. toctree::
   :maxdepth: 2

   source <source/modules>

##################
Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
