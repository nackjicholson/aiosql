Defining SQL Queries
====================

Query Names
-----------

Name definitions are how aiosql determines the name of the methods that SQL
code blocks are accessible by.
A query name is defined by a SQL comment of the form ``"-- name: "``.
As a readability convenience, dash characters (``-``) in the name are turned
into underlines (``_``).

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 14,16

This query will be available in aiosql under the python method name ``.get_all_blogs(conn)``

Query Comments
--------------

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 14-16

Any other SQL comments you make between the name definition and your code will
be used a the python documentation string for the generated method.
You can use ``help()`` in the Python REPL to view these comments while using python.

..
   FIXME method parameters are not shown…

.. code:: pycon

    Python 3 … on Linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import aiosql
    >>> queries = aiosql.from_path("blogs.sql", "sqlite3")
    >>> help(queries.get_all_blogs)
    Help on method get_all_blogs in module aiosql.queries:

    get_all_blogs(conn, *args, **kwargs) method of aiosql.queries.Queries instance
        Fetch all fields for every blog in the database.

Named Parameters
----------------

Named parameters ``:param`` are accepted by all supported drivers and taken
from Python named parameters passed to the query.
In addition, simple attributes can be referenced with the ``.``-syntax.

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 61-62

Then the generated function expects two named parameters:

.. code:: python

    res = queries.with_params(name="Calvin", x=(1+1j))
    # => (6, 2.0)

Parameter Declarations
----------------------

Query parameter names may be declared in parentheses just after the method name.

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 55,56

When declared they are checked, raising errors when parameters are unused or undeclared.

Operators
---------

This section describes the usage of various query operator symbols that you can
annotate query names with in order to direct how aiosql will execute and return
results.

No Operator (Default)
~~~~~~~~~~~~~~~~~~~~~

In the above `Query Names <#query-names>`__ section the ``get-all-blogs``
name is written without any trailing operators.

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 14

The lack of an explicit operator tells aiosql to execute the query and
to return **all** the results.
In the case of ``get-all-blogs`` that means a ``select`` statement will be
executed and all the resulting rows will be returned.
When writing your application you will often need to perform other operations
besides ``select``, like ``insert``, ``delete``, and perhaps bulk operations.
The operators detailed in the next sections let you declare in your SQL code
how that query should be executed by a Python database driver.

``^`` Select One
~~~~~~~~~~~~~~~~

The ``^`` operator executes a query and returns the **first row** of a result set.
When there are no rows in the result set it returns ``None``.
This is useful when you know there should be one, and exactly one result from your query.

As an example, if you have a unique constraint on the ``username`` field in your
``users`` table which makes it impossible for two users to share the same username,
you could use ``^`` to direct aiosql to select a single user rather than a list of
rows of length 1.

.. literalinclude:: ../../tests/blogdb/sql/users/users.sql
   :language: sql
   :lines: 8-14

When used from Python this query will either return ``None`` or the singular selected row.

.. code:: python

    queries.get_user_by_username(conn, username="willvaughn")
    # => (1, "willvaughn", "William Vaughn") or None

``$`` Select Value
~~~~~~~~~~~~~~~~~~

The ``$`` operator will execute the query, and only return the **first value of the first row**
of a result set. If there are no rows in the result set it returns ``None``.
This is implemented by returing the first element of the tuple returned by ``cur.fetchone()``
from the underlying driver.
This is mostly useful for queries returning IDs, COUNTs or other aggregates.

.. literalinclude:: ../../tests/blogdb/sql/users/users.sql
   :language: sql
   :lines: 30,32

When used from Python:

.. code:: python

    queries.get_count(conn)
    # => 3 or None

``!`` Insert/Update/Delete
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``!`` operator executes SQL without returning any results.
It is meant for statements that use ``insert``, ``update``, and ``delete`` to make
modifications to database rows without a necessary return value.

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 64-66,32,34

The methods generated are:

.. code:: python

    def new_blog(conn, userid: int, title: str, content: str) -> int:
        pass

    def remove_blog(conn, blogid: int) -> int:
        pass

Each can be called to alter the database, and returns the number of affected rows
if available.

Note that some SQL databases allow to return a relation after ``insert``,
``update`` or ``delete`` by using a ``returning`` clause.
For such queries the result is a relation like a ``select``, so the same operators
apply:

.. literalinclude:: ../../tests/blogdb/sql/blogs/blogs.sql
   :language: sql
   :lines: 68-71

.. code:: python

    blogid = queries.publish_new_blog(conn, userid=1, title="AioSQL New Features", content="…")

``<!`` Insert/Update/Delete Implicit Returning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When performing a modification of rows, or adding new rows, sometimes it is
necessary to return values using the ``returning`` clause where available,
as described above.

When using old versions of SQLite this special operator will return the id of
the inserted row using
```cur.lastrowid`` <https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.lastrowid>`__.

As recent version of SQLite do support the ``returning`` clause, simply forget
about this, use the clause explicitely and treat the whole command as a standard
select with the *empty* operator (relation), or ``^`` (tuple), or ``$`` (scalar).

.. literalinclude:: ../../tests/blogdb/sql/blogs/li/blogs.sql
   :language: sql
   :lines: 39-41

Executing this query in python will return the ``blogid`` of the inserted row.

.. code:: python

    blogid = queries.publish_a_blog(conn, userid=1, title="Hi", content="blah blah.")

``*!`` Insert/Update/Delete Many
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``*!`` operator directs aiosql to execute a SQL statement over all items of a given sequence.
Under the hood this calls the ``executemany`` method of many database drivers.
See `sqlite3 Cursor.executemany <https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.executemany>`__
for an example.

In aiosql we can use this for a bulk publish method that operates over a list of blog entries.

.. literalinclude:: ../../tests/blogdb/sql/blogs/pg/blogs.sql
   :language: sql
   :lines: 50-53

.. code:: python

    queries = aiosql.from_path("blogs.sql", "psycopg2")
    blogs = [
        {"userid": 1, "title": "First Blog", "content": "...", "published": datetime(2018, 1, 1)},
        {"userid": 1, "title": "Next Blog", "content": "...", "published": datetime(2018, 1, 2)},
        {"userid": 2, "title": "Hey, Hey!", "content": "...", "published": datetime(2018, 7, 28)},
    ]
    queries.bulk_publish(conn, blogs)

The methods returns the number of affected rows, if available.

``#`` Execute Scripts
~~~~~~~~~~~~~~~~~~~~~

Using this operarator will execute sql statements as a script.
You can't do variable substitution with the ``#`` operator.
An example usecase is using data definition statements like create table in order to setup a database.

.. literalinclude:: ../../tests/blogdb/sql/blogs/pg/blogs.sql
   :language: sql
   :lines: 9-16

.. code:: python

    queries = aiosql.from_path("create_schema.sql", "sqlite3")
    queries.create_table_blogs(conn)

Note: SQL scripts do not accept parameters.
