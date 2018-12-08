####################
Defining SQL Queries
####################

Query Names & Comments
======================

Name definitions are how ``aiosql`` determines how to name the SQL code blocks which are loaded.
A query name definition is a normal SQL comment starting with "-- name:" and is followed by the
name of the query. You can use ``-`` or ``_`` in your query names, but the methods in python
will always be valid python names using underscores.

.. code-block:: sql

    -- name: get-all-blogs
    select * from blogs;

The above example when loaded by ``aiosql.from_path`` will return an object with a
``.get_all_blogs(conn)`` method.

Your SQL comments will be added to your methods as python documentation, and accessible by calling
``help()`` on them.

.. code-block:: sql

    -- name: get-all-blogs
    -- Fetch all fields for every blog in the database.
    select * from blogs;


.. code-block:: python

    queries = aiosql.from_path("blogs.sql", "sqlite3")
    help(aiosql.get_all_blogs)

output

.. code-block:: text

    Help on function get_user_blogs in module aiosql.aiosql:

    get_all_blogs(conn, *args, **kwargs)
        Fetch all fields for every blog in the database.

Query Operations
================

Adding query operator symbols to the end of query names will inform ``aiosql`` of how to
execute and return results. In the above section the ``get-all-blogs`` name has no special operator
characters trailing it. This lack of operator is actually the most basic operator which performs
SQL ``select`` statements and returns a list of rows. When writing an application you will often
need to perform other operations besides selects, like inserts, deletes, and bulk opearations. The
operators detailed in this section let you declare in your SQL, how your code should be executed
by the database driver.

Insert/Update/Delete with ``!``
-------------------------------

The ``!`` operator will execute SQL without returning any results. It is meant for use with ``insert``,
``update``, and ``delete`` statements for which returned data is not required.

.. code-block:: sql

    -- name: publish-blog!
    insert into blogs(userid, title, content) values (:userid, :title, :content);

    -- name: remove-blog!
    -- Remove a blog from the database
    delete from blogs where blogid = :blogid;


The methods generated are:

    - ``publish_blog(conn, *args, **kwargs)``
    - ``remove_blog(conn, *args, **kwargs)``

Each of them can be run to alter the database, but both will return ``None``.

Insert Returning with ``<!``
----------------------------

Sometimes when performing an insert it is necessary to receive some information back about the
newly created database row. The ``<!`` operator tells aiosql to perform execute the insert query, but to also expect and
return some data.

In SQLite this means the ``cur.lastrowid`` will be returned.

.. code-block:: sql

    -- name: publish-blog<!
    insert into blogs(userid, title, content) values (:userid, :title, :content);

Will return the ``blogid`` of the inserted row.

PostgreSQL however allows returning multiple values via the ``returning`` clause of insert
queries.

.. code-block:: sql

    -- name: publish-blog<!
    insert into blogs (
        userid,
        title,
        content
    )
    values (
        :userid,
        :title,
        :content
    )
    returning blogid, title;

This will insert the new blog row and return both it's ``blogid`` and ``title`` value as follows::

    queries = aiosql.from_path("blogs.sql", "psycopg2")
    blogid, title = queries.publish_blog(conn, userid=1, title="Hi", content="word.")

Insert/Update/Delete Many with ``*!``
-------------------------------------

The DB-API 2.0 drivers like ``sqlite3`` and ``psycopg2`` have an ``executemany`` method which
execute a SQL command against all parameter sequences or mappings found in a sequence. This
is useful for bulk updates to the database. The below example is a PostgreSQL statement to insert
many blog rows.

.. code-block:: sql

    -- name: bulk-publish*!
    -- Insert many blogs at once
    insert into blogs (
        userid,
        title,
        content,
        published
    )
    values (
        :userid,
        :title,
        :content,
        :published
    )

Applying this to a list of blogs in python::

    queries = aiosql.from_path("blogs.sql", "psycopg2")
    blogs = [
        {"userid": 1, "title": "First Blog", "content": "...", published: datetime(2018, 1, 1)},
        {"userid": 1, "title": "Next Blog", "content": "...", published: datetime(2018, 1, 2)},
        {"userid": 2, "title": "Hey, Hey!", "content": "...", published: datetime(2018, 7, 28)},
    ]
    queries.bulk_publish(conn, blogs)

Execute SQL script statements with ``#``
---------------------------------------------

Executes some sql statements as a script. These methods don't do variable substitution, or return
any rows. An example usecase is using data definition statements like create table in order to
setup your database.

.. code-block:: sql

    -- name: create-schema#
    create table users (
        userid integer not null primary key,
        username text not null,
        firstname integer not null,
        lastname text not null
    );

    create table blogs (
        blogid integer not null primary key,
        userid integer not null,
        title text not null,
        content text not null,
        published date not null default CURRENT_DATE,
        foreign key(userid) references users(userid)
    );

From code::

    queries = aiosql.from_path("create_schema.sql", "sqlite3")
    queries.create_schema(conn)

