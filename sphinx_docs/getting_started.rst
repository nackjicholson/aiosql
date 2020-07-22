###############
Getting Started
###############

Basic Usage
===========

Given you have a SQL file like the one below called ``users.sql``

.. code-block:: sql

    -- name: get-all-users
    -- Get all user records
    select * from users;


    -- name: get-user-by-username
    -- Get user with the given username field.
    select userid,
           username,
           firstname,
           lastname
      from users
     where username = :username;

You can use ``aiosql`` to load the queries in this file for use in your Python application:

.. code-block:: python

    import aiosql
    import sqlite3

    conn = sqlite3.connect("myapp.db")
    queries = aiosql.from_path("users.sql", "sqlite3")

    users = queries.get_all_users(conn)
    # >>> [(1, "nackjicholson", "William", "Vaughn"), (2, "johndoe", "John", "Doe"), ...]

    users = queries.get_user_by_username(conn, username="nackjicholson")
    # >>> [(1, "nackjicholson", "William", "Vaughn")

This is pretty nice, we're able to define our methods in SQL and use them as methods from python!

Query Operators
===============

``aiosql`` can help you do even more by allowing you to declare in the SQL how you would like a query to be executed
and returned in python. For instance, the ``get-user-by-username`` query above should really only return a single result
instead of a list containing one user. With the raw ``sqlite3`` driver in python we would probably have used
``cur.fetchone()`` instead of `cur.fetchall()` to retrieve a single row. We can inform ``aiosql`` to select a single row
by using the ``^`` (select one) operator on the end of our query name.

.. code-block:: sql
    -- name: get-user-by-username^
    -- Get user with the given username field.
    select userid,
           username,
           firstname,
           lastname
      from users
     where username = :username;

.. code-block:: python

    nack = queries.get_user_by_username(conn, username="nackjicholson")
    # >>> (1, "nackjicholson", "William", "Vaughn")

Python Domain Objects
=====================

Using your own python types for SQL data is possible by declaring a `record_class` directive for a query. This informs
``aiosql`` that it should marshal our data to be held by a python class. In python3.7 a good choice for this is the new
``dataclass`` package. You can also easily use ``typing.NamedTuple``, ``collections.namedtuple``, or any other python
class. It's up to you!

.. code-block:: sql

    -- name: get-user-by-username^
    -- record_class: User
    -- Get user with the given username field.
    select userid,
           username,
           firstname,
           lastname
      from users
     where username = :username;

All we have to do is provide our custom type to ``aiosql`` when we load our queries via the ``record_classes`` argument.

.. code-block:: python

    import aiosql
    import sqlite3
    from dataclasses import dataclass


    @dataclass
    class User:
        userid: int
        username: str
        firstname: str
        lastname: str


    conn = sqlite3.connect("myapp.db")
    queries = aiosql.from_path("users.sql", "sqlite3", record_classes={"User": User})

    nack = queries.get_user_by_username(conn, username="nackjicholson")
    # >>> User(userid=1, username="nackjicholson", firstname="William", lastname="Vaughn")

Hopefully this is enough to intrigue you and entice you to give aiosql a try. Happy SQLing!

Queries Type Hinting
====================

Because the ``aiosql.Queries`` instance is dynamically bound with methods loaded from the directives in your ``.sql``
files, IDEs and editors can't statically analyze your ``Queries`` instance in order to provide you with helpful
method auto-completion or interface information.

Python 3.6 gives us a way to fix this if we'd like by providing a type annotation. This can be very helpful, but beware
it can also become a bit of a maintenance burden because we have to keep the type annotation up to date with any changes
we make to our ``.sql`` code. It's up to you whether the IDE tooling and type information is worth it to you.

.. code-block:: python

    from typing import List, Optional

    class QInterface:
        def get_all_users(conn) -> List[User]:
            pass

        def get_user_by_username(conn, username: str) -> Optional[User]:
            pass


    queries: QInterface = aiosql.from_path("...")

