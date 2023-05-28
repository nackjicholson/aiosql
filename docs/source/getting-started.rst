Getting Started
===============

Philosophy
----------

The aiosql project is for writing SQL to interact with a database.
Most database libraries are intended to reduce the amount of SQL developers need to write,
aiosql takes an alternative approach.
Why?

-  Alternatives are good. No approach fits all use cases, no matter how predominant.
-  SQL is the most expressive and performant way to interact with a SQL database.
-  Investigating where a query came from is simpler when it is source controlled, named, and written by a human.
-  Writing SQL in files gives you built-in compatibility with powerful SQL tools like `DataGrip <https://www.jetbrains.com/datagrip/>`__ and `psql <https://www.postgresql.org/docs/12/app-psql.html>`__.

About ORMs
~~~~~~~~~~

ORMs and SQL Query Builders offer object interfaces to generate and execute SQL.
They exist to ease development, not to make it simpler.
Inheriting object hierarchies, mixing data with behaviors, mirroring a database schema, and generating SQL are not simple.
ORMs are introduced early in a project's life when requirements are limited and the need to move fast is paramount.
As a project grows, ORM objects and their relations grow too, they become a source of complexity and coupling.

``aiosql`` doesn't solve these problems directly either, your application will still get more complex with time.
You can write bad SQL and bad python.
But, with aiosql there is no mandate that all interaction with the database go
through a complex network of related python objects that mirror a database schema.
The only mandates are that you write SQL to talk to the database and python to use the data.
From there you start with a system in which the database and the application are intentionally
separate and independent from each other so they can change independently.
The architecture of your application and the boundaries you choose between it and the database is left to you.

The documentation for projects like `SQLAlchemy <https://www.sqlalchemy.org/>`__ and
`Django DB <https://www.djangoproject.com/>`__ can give you a better vision
for the class of problems that ORMs do solve and the productivity gains they intend.
Please choose these projects over ``aiosql`` if you find that they fit the needs of your application better.

Loading Queries
---------------

This section goes over the three ways to make SQL queries available for execution in python.
You'll learn the basics of defining queries so aiosql can find them and turn them into methods
on a ``Queries`` object.
For more details reference the :doc:`defining-sql-queries` documentation.

From a SQL File
~~~~~~~~~~~~~~~

SQL can be loaded by providing a path to a ``.sql`` file.
Below is a *blogs.sql* file that defines two queries.

.. code:: sql

    -- name: get_all_blogs
    select blogid,
           userid,
           title,
           content,
           published
      from blogs;

    -- name: get_user_blogs
    -- Get blogs with a fancy formatted published date and author field
        select b.blogid,
               b.title,
               strftime('%Y-%m-%d %H:%M', b.published) as published,
               u.username as author
          from blogs b
    inner join users u on b.userid = u.userid
         where u.username = :username
      order by b.published desc;

Notice the ``-- name: <name_of_method>`` comments and the ``:username`` substitution variable.
The comments that start with ``-- name:`` are the magic of aiosql.
They are used by ```aiosql.from_path`` <./api.md#aiosqlfrom_path>`__ to parse the file
into separate methods accessible by the name.
The ``aiosql.from_path`` function takes a path to a sql file or directory
and the name of the database driver intended for use with the methods.

.. code:: python

    queries = aiosql.from_path("blogs.sql", "sqlite3")

In the case of *blogs.sql* we expect the following two methods to be available.
The ``username`` parameter of ``get_user_blogs`` will substitute in for the ``:username`` variable in the SQL.

.. code:: python

    def get_all_blogs(self) -> List:
        pass

    def get_user_blogs(self, username: str) -> List:
        pass

From an SQL String
~~~~~~~~~~~~~~~~~~

SQL can be loaded from a string as well.
The result below is the same as the first example above that loads from a SQL file.

.. code:: python

    sql_str = """
    -- name: get_all_blogs
    select blogid,
           userid,
           title,
           content,
           published
      from blogs;

    -- name: get_user_blogs
    -- Get blogs with a fancy formatted published date and author field
        select b.blogid,
               b.title,
               strftime('%Y-%m-%d %H:%M', b.published) as published,
               u.username as author
          from blogs b
    inner join users u on b.userid = u.userid
         where u.username = :username
      order by b.published desc;
    """

    queries = aiosql.from_str(sql_str, "sqlite3")

The ``Queries`` object here will have two methods:

.. code:: python

    queries.get_all_blogs(conn)
    queries.get_user_blogs(conn, username="johndoe")

From a Directory of SQL Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loading a directory of SQL files loads all of the queries defined in those files into a single object.
The ``example/sql`` directory below contains three ``.sql`` files and can be loaded using
``aiosql.from_path`` `<./api.md#aiosqlfrom_path>`__.

::

    example/sql
    ├── blogs.sql
    ├── create_schema.sql
    └── users.sql

.. code:: python

    queries = aiosql.from_path("example/sql", "sqlite3")

The resulting ``queries`` object will have a mixture of methods from all the files.

.. warning::

    Don't name queries the same in various files in the same directory.
    The last one loaded will win.
    See :ref:`subdirectories` below to namespace queries.


Subdirectories
^^^^^^^^^^^^^^

Introducing subdirectories allows namspacing queries.
This provides a way to further organize and group queries conceptually.
For instance, you could define blog queries separate from user queries access them on distinct
properties of the queries object.

Assume the *blogs.sql* and *users.sql* files both contain a ``-- name: get_all`` query.

::

    example/sql
    ├── blogs
    │   └── blogs.sql
    ├── create_schema.sql
    └── users
        └── users.sql

.. code:: python

    queries = aiosql.from_path("example/sql", "sqlite3")

The ``Queries`` object has two nested ``get_all`` methods accessible on attributes ``.blogs`` and ``.users``.
The attributes reflect the names of the subdirectories.

.. code:: python

    queries.blogs.get_all(conn)
    queries.users.get_all(conn)

Calling Query Methods
---------------------

Connections
~~~~~~~~~~~

The connection or ``conn`` is always the first argument to an ``aiosql`` method.
The ``conn`` is an open connection to a database driver that your aiosql method can use for executing the sql it contains.
Controlling connections outside of aiosql queries means you can call multiple queries and control them under one transaction,
or otherwise set connection level properties that affect driver behavior.

.. note::

    For more see: :ref:`leveraging-driver-specific-features`.

In the examples throughout this page a ``conn`` object has been passed.
Here is a more code complete example that shows the connection creation and call to
``aiosql.from_path`` `<./api.md#aiosqlfrom_path>`__ that make a queries object.

.. code:: pycon

    >>> import sqlite3
    >>> import aiosql
    >>> conn = sqlite3.connect("./mydb.sql")
    >>> # Note the "sqlite3" driver_adapter argument is what tells 
    >>> # aiosql it should be expecting a sqlite3 connection object.
    >>> queries = aiosql.from_path("./blogs.sql", "sqlite3")
    >>> queries.get_all_blogs(conn)
    [(1,
      1,
      'What I did Today',
      'I mowed the lawn, washed some clothes, and ate a burger.\n'
      '\n'
      'Until next time,\n'
      'Bob',
      '2017-07-28'),
     (2, 3, 'Testing', 'Is this thing on?\n', '2018-01-01'),
     (3,
      1,
      'How to make a pie.',
      '1. Make crust\n2. Fill\n3. Bake\n4. Eat\n',
      '2018-11-23')]

Passing Parameters
~~~~~~~~~~~~~~~~~~

.. code:: sql

    -- name: get_user_blogs
    -- Get blogs with a fancy formatted published date and author field
        select b.blogid,
               b.title,
               strftime('%Y-%m-%d %H:%M', b.published) as published,
               u.username as author
          from blogs b
    inner join users u on b.userid = u.userid
         where u.username = :username
      order by b.published desc;

``aiosql`` allows parameterization of queries by parsing values like ``:username``
in the above query and having the resultant method expect an inbound argument to
substitute for ``:username``.

You can call the ``get_user_blogs`` function with plain arguments or keyword arguments with the
name of the subsitution variable.

.. code:: python

    >>> import sqlite3
    >>> import aiosql
    >>> conn = sqlite3.connect("./mydb.sql")
    >>> queries = aiosql.from_path("./blogs.sql", "sqlite3")
    >>>
    >>> # Using keyword args
    >>> queries.get_user_blogs(conn, username="bobsmith")
    [(3, 'How to make a pie.', '2018-11-23 00:00', 'bobsmith'), (1, 'What I did Today', '2017-07-28 00:00', 'bobsmith')]
    >>>
    >>> # Using positional argument
    >>> queries.get_user_blogs(conn, "janedoe")
    [(2, 'Testing', '2018-01-01 00:00', 'janedoe')]

.. warning::

    When passing positional arguments aiosql will apply them in the order that the substitutions appear in your SQL.
    This can be convenient and clear in some cases, but confusing in others.
    You might want to choose to always name your arguments for clarity.
