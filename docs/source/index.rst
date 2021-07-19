.. aiosql documentation master file, created by
   sphinx-quickstart on Sun Jul 18 12:49:31 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiosql - Simple SQL in Python
==================================

SQL is code. Write it, version control it, comment it, and run it using files. Writing your SQL code in Python programs as strings doesn't allow you to easily reuse them in SQL GUIs or CLI tools like psql. With aiosql you can organize your SQL statements in *.sql* files, load them into your python application as methods to call without losing the ability to use them as you would any other SQL file.

This project supports standard and `asyncio <https://docs.python.org/3/library/asyncio.html>`__ based
drivers for SQLite and PostgreSQL out of the box (`sqlite3 <https://docs.python.org/3/library/sqlite3.html>`__, `aiosqlite <https://aiosqlite.omnilib.dev/en/latest/?badge=latest>`__, `psycopg2 <https://www.psycopg.org/docs/>`__, `asyncpg <https://magicstack.github.io/asyncpg/current/>`__). Extensions to support other database drivers can be written by you! See: `Database Driver Adapters <./database-driver-adapters.md>`__

.. danger::

    This project supports `asyncio <https://docs.python.org/3/library/asyncio.html>`__ based drivers and requires python versions >3.6.

Badges
------

.. image:: https://github.com/nackjicholson/aiosql/actions/workflows/aiosql-package.yml/badge.svg?branch=master

Installation
------------

.. code:: sh

    pip install aiosql

Or if you you use `poetry <https://python-poetry.org>`__:

.. code:: sh

    poetry add aiosql

Usage
-----

*users.sql*

.. code:: sql

    -- name: get-all-users
    -- Get all user records
    select userid,
           username,
           firstname,
           lastname
      from users;


    -- name: get-user-by-username^
    -- Get user with the given username field.
    select userid,
           username,
           firstname,
           lastname
      from users
     where username = :username;

You can use ``aiosql`` to load the queries in this file for use in your Python application:

.. code:: python

    import aiosql
    import sqlite3

    conn = sqlite3.connect("myapp.db")
    queries = aiosql.from_path("users.sql", "sqlite3")

    users = queries.get_all_users(conn)
    # >>> [(1, "nackjicholson", "William", "Vaughn"), (2, "johndoe", "John", "Doe"), ...]

    users = queries.get_user_by_username(conn, username="nackjicholson")
    # >>> (1, "nackjicholson", "William", "Vaughn")

Writing SQL in a file and executing it from methods in python!

Async Usage
-----------

*greetings.sql*

.. code:: sql

    -- name: get_all_greetings
    -- Get all the greetings in the database
    select greeting_id, greeting from greetings;

    -- name: get_user_by_username^
    -- Get a user from the database
    select user_id,
           username,
           name
      from users
     where username = :username;

*example.py*

.. code:: python

    import asyncio
    import aiosql
    import aiosqlite


    queries = aiosql.from_path("./greetings.sql", "aiosqlite")


    async def main():
        # Parallel queries!!!
        async with aiosqlite.connect("greetings.db") as conn:
            greetings, user = await asyncio.gather(
                queries.get_all_greetings(conn),
                queries.get_user_by_username(conn, username="willvaughn")
            )
            # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
            # user = (1, "willvaughn", "William")

            for _, greeting in greetings:
                print(f"{greeting}, {user[2]}!")
            # Hi, William!
            # Aloha, William!
            # Hola, William!

    asyncio.run(main())

This example has an imaginary SQLite database with greetings and users. It prints greetings in various languages to the user and showcases the basic feature of being able to load queries from a sql file and call them by name in python code. It also happens to do two SQL queries in parallel using ``aiosqlite`` and asyncio.

Why you might want to use this
------------------------------

* You think SQL is pretty good, and writing SQL is an important part of your applications.
* You don't want to write your SQL in strings intermixed with your python code.
* You're not using an ORM like SQLAlchemy or Django, and you don't need to.
* You want to be able to reuse your SQL in other contexts. Loading it into psql or other database tools.

Why you might NOT want to use this
----------------------------------

* You're looking for an ORM.
* You aren't comfortable writing SQL code.
* You don't have anything in your application that requires complicated SQL beyond basic CRUD operations.
* Dynamically loaded objects built at runtime really bother you.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Getting Started <getting-started>
   Defining SQL Queries <defining-sql-queries>
   Advanced Topics <advanced-topics>
   Database Driver Adapters <database-driver-adapters>
   Contributing <contributing>
   API <pydoc/modules>
