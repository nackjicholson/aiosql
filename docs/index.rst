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

This project supports python versions >3.6 because it supports ``asyncio`` database drivers for SQLite and PostgreSQL
out of the box, and can be extended to support other database types. If you are using other versions of python please
see the related `anosql <https://github.com/honza/anosql>`_ package which this project is based on.

Contents
========

.. toctree::
   :maxdepth: 2

   Install <install>
   Getting Started <getting_started>
   Defining Queries <defining_queries>
   Extending aiosql to additional database drivers <query_loaders>
   API <source/modules>

Quick Example
=============

*greetings.sql*

.. code-block:: sql

    -- name: get-all-greetings
    -- Get all the greetings in the database
    select * from greetings;

    -- name: $get-users-by-username
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

    queries = aiosql.from_path("greetings.sql", db_driver="aiosqlite")

    async def main():
       # Parallel queries!!!
       with async aiosqlite.connect("greetings.db") as conn:
           greetings, users = await asyncio.gather(
               queries.get_all_greetings(conn),
               queries.get_users_by_username(conn, username="willvaughn")
           )
           # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
           # users = [{"user_id": 1, "username": "willvaughn", "name": "Will"}]

    asyncio.run(main())

##################
Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
