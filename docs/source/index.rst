aiosql - Simple SQL in Python (aka YeSQL for Python)
====================================================

`SQL <https://en.wikipedia.org/wiki/SQL>`__ is code.
Write it, version control it, comment it, and run it using files.
Writing your SQL code in Python programs as strings doesn't allow you to easily
reuse them in SQL GUIs or CLI tools like ``psql``.
With aiosql you can organize your SQL statements in *.sql* files, load them
into your python application as methods to call without losing the ability to
use them as you would any other SQL file.

This project supports standard
`PEP 249 <https://peps.python.org/pep-0249/>`__
and
`asyncio <https://docs.python.org/3/library/asyncio.html>`__
based drivers for
`SQLite <https://www.sqlite.org/>`__
(`sqlite3 <https://docs.python.org/3/library/sqlite3.html>`__,
`aiosqlite <https://aiosqlite.omnilib.dev/en/latest/?badge=latest>`__,
`apsw <https://pypi.org/project/apsw/>`__),
`PostgreSQL <https://postgresql.org/>`__
(`psycopg (3) <https://www.psycopg.org/psycopg3/>`__,
`apsycopg (3) <https://www.psycopg.org/psycopg3/>`__,
`psycopg2 <https://www.psycopg.org/docs/>`__,
`pg8000 <https://pypi.org/project/pg8000/>`__,
`pygresql <http://www.pygresql.org/>`__,
`asyncpg <https://magicstack.github.io/asyncpg/current/>`__),
`MySQL <https://www.mysql.com/>`__
(`PyMySQL <https://github.com/PyMySQL/PyMySQL/>`__,
`mysqlclient <https://pypi.org/project/mysqlclient/>`__,
`mysql-connector <https://dev.mysql.com/doc/connector-python/en/>`__,
`asyncmy <https://github.com/long2ice/asyncmy>`__ with
`this adapter <https://github.com/GoogleCloudPlatform/database-assessment/blob/main/src/dma/lib/db/adapters/asyncmy.py>`__),
`MariaDB <https://mariadb.org/>`__
(`mariadb <https://pypi.org/project/mariadb/>`__),
`DuckDB <https://www.duckdb.org/>`__
(`duckdb <https://duckdb.org/docs/api/python/dbapi>`__) and
`MS SQL Server <https//en.wikipedia.org/wiki/Microsoft_SQL_Server>`__
(`pymssql <https://pypi.org/project/pymssql/>`__),
However, some detailed feature support may vary depending on the underlying driver
and database engine actual capabilities.

Other SQL database drivers which support the ``pyformat`` or ``named``
`PEP 249 <https://peps.python.org/pep-0249/>`__ paramstyles should work as well
by just passing the driver as a parameter when building queries.  Thus
`Oracle Database <https://en.wikipedia.org/wiki/Oracle_Database>`__
(`oracledb <https://oracle.github.io/python-oracledb/>`__) or
`Snowflake <https://en.wikipedia.org/wiki/Snowflake_Inc.>`__
(`snowflake.connector <https://docs.snowflake.com/en/developer-guide/python-connector/python-connector>`__)
should work out of the box…
Please report with an issue if it actually works for you!
Otherwise, extensions to support other database drivers can be written by you!
See: `Database Driver Adapters <./database-driver-adapters.html>`__.
Feel free to pull request!

This module is an implementation of
`Kris Jenkins' yesql <https://github.com/krisajenkins/yesql>`__
`Clojure <https://clojure.org/>`__ library to the
`Python <https://www.python.org/>`__
`ecosystem <https://pypi.org/>`__.

Badges
------

..
   NOTE :target: is needed so that github renders badges on a line.
.. image:: https://github.com/nackjicholson/aiosql/actions/workflows/aiosql-package.yml/badge.svg?branch=main&style=flat
   :alt: Build status
   :target: https://github.com/nackjicholson/aiosql/actions/
..
   NOTE hardcoded, this is maintained manually.
.. image:: https://img.shields.io/badge/coverage-100%25-success
   :alt: Code Coverage
   :target: https://github.com/nackjicholson/aiosql/actions/
..
   NOTE all tests
   # MISC
   loading: 17
   patterns: 6
   # SYNC
   sqlite3: 17
   apsw: 16
   duckdb: 15
   mariadb: 17
   pymysql: 16
   mysqldb: 15
   myco: 16
   pymssql: 16
   pg8000: 14
   psycopg2: 18
   psycopg3: 19
   pygresql: 15
   # ASYNC
   aiosqlite: 13
   asyncpg: 18
   apsycopg3: 14
.. image:: https://img.shields.io/badge/tests-262%20✓-success
   :alt: Tests
   :target: https://github.com/nackjicholson/aiosql/actions/
.. image:: https://img.shields.io/github/issues/nackjicholson/aiosql?style=flat
   :alt: Issues
   :target: https://github.com/nackjicholson/aiosql/issues/
.. image:: https://img.shields.io/github/contributors/nackjicholson/aiosql
   :alt: Contributors
   :target: https://github.com/nackjicholson/aiosql/graphs/contributors
.. image:: https://img.shields.io/pypi/dm/aiosql?style=flat
   :alt: Pypi Downloads
   :target: https://pypistats.org/packages/aiosql
.. image:: https://img.shields.io/github/stars/nackjicholson/aiosql?style=flat&label=Star
   :alt: Stars
   :target: https://github.com/nackjicholson/aiosql/stargazers
.. image:: https://img.shields.io/pypi/v/aiosql
   :alt: Version
   :target: https://pypi.org/project/aiosql/
.. image:: https://img.shields.io/github/languages/code-size/nackjicholson/aiosql?style=flat
   :alt: Code Size
   :target: https://github.com/nackjicholson/aiosql/
.. image:: https://img.shields.io/badge/databases-6-informational
   :alt: Databases
   :target: https://github.com/nackjicholson/aiosql/
.. image:: https://img.shields.io/badge/drivers-16-informational
   :alt: Drivers
   :target: https://github.com/nackjicholson/aiosql/
.. image:: https://img.shields.io/github/languages/count/nackjicholson/aiosql?style=flat
   :alt: Language Count
   :target: https://en.wikipedia.org/wiki/Programming_language
.. image:: https://img.shields.io/github/languages/top/nackjicholson/aiosql?style=flat
   :alt: Top Language
   :target: https://en.wikipedia.org/wiki/Python_(programming_language)
.. image:: https://img.shields.io/pypi/pyversions/aiosql?style=flat
   :alt: Python Versions
   :target: https://www.python.org/
..
   NOTE some non-sense badge about badges:-)
.. image:: https://img.shields.io/badge/badges-16-informational
   :alt: Badges
   :target: https://shields.io/
.. image:: https://img.shields.io/pypi/l/aiosql?style=flat
   :alt: BSD 2-Clause License
   :target: https://opensource.org/licenses/BSD-2-Clause


Usage
-----

Install from `pypi <https://pypi.org/project/aiosql>`__, for instance by running ``pip install aiosql``.

Then write parametric SQL queries in a file and execute it from Python methods,
eg this *greetings.sql* file:

.. code:: sql

    -- name: get_all_greetings()
    -- Get all the greetings in the database
    select greeting_id, greeting
      from greetings
     order by 1;

    -- name: get_user_by_username(username)^
    -- Get a user from the database using a named parameter
    select user_id, username, name
      from users
      where username = :username;

This example has an imaginary SQLite database with greetings and users.
It prints greetings in various languages to the user and showcases the basic
feature of being able to load queries from a SQL file and call them by name
in python code.
Query parameter declarations (eg ``(username)``) are optional, and enforced
when provided.

You can use ``aiosql`` to load the queries in this file for use in your Python
application:

.. code:: python

    import aiosql
    import sqlite3

    queries = aiosql.from_path("greetings.sql", "sqlite3")

    with sqlite3.connect("greetings.db") as conn:
        user = queries.get_user_by_username(conn, username="willvaughn")
        # user: (1, "willvaughn", "William")

        for _, greeting in queries.get_all_greetings(conn):
            # scan: (1, "Hi"), (2, "Aloha"), (3, "Hola"), …
            print(f"{greeting}, {user[2]}!")
        # Hi, William!
        # Aloha, William!
        # …

Or even in an asynchroneous way, with two SQL queries running in parallel
using ``aiosqlite`` and ``asyncio``:

.. code:: python

    import asyncio
    import aiosql
    import aiosqlite

    queries = aiosql.from_path("greetings.sql", "aiosqlite")

    async def main():
        async with aiosqlite.connect("greetings.db") as conn:
            user = await queries.get_user_by_username(conn, username="willvaughn")

            async for _, greeting in queries.get_all_greetings(conn):
                print(f"{greeting}, {user[2]}!")

    asyncio.run(main())

It may seem inconvenient to provide a connection on each call.
You may have a look at the `AnoDB <https://github.com/zx80/anodb>`__ `DB`
class which wraps both a database connection *and* queries in one
connection-like extended object, including performing automatic reconnection
when needed. The wrapper also allows to cache query results.

Why you might want to use this
------------------------------

* You think SQL is pretty good, and writing SQL is an important part of your applications.
* You don't want to write your SQL in strings intermixed with your python code.
* You're not using an ORM like `SQLAlchemy <https://www.sqlalchemy.org/>`__ or
  `Django <https://www.djangoproject.com/>`__ ,
  with large (100k lines) code imprints vs under 1000 for `aiosql` and about 300 for `anodb`,
  and you don't need to or don't want to write SQL-like code with a Python syntax.
* You want to be able to reuse your SQL in other contexts,
  eg loading it into `psql` or other database tools.


Why you might NOT want to use this
----------------------------------

* You're looking for an `ORM <https://en.wikipedia.org/wiki/Object-relational_mapping>`__.
* You aren't comfortable writing SQL code.
* You don't have anything in your application that requires complicated SQL beyond basic CRUD operations.
* Dynamically loaded objects built at runtime really bother you.
