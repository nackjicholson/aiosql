Advanced Topics
===============

Accessing the ``cursor`` object
-------------------------------

The cursor is a temporary object created in memory that allows you to perform
row-by-row operations on your data and use handy methods such as
``.description``, ``.fetchall()`` and ``.fetchone()``.
As long as you are running a SQL ``SELECT`` query, you can access the cursor
object by appending ``_cursor`` to the end of the queries name.

For example, say you have the following query named ``get-all-greetings`` in a ``sql`` file:

.. literalinclude:: ../../example/greetings.sql
   :language: sql
   :lines: 1-5

With this query, you can get all ``greeting_id``'s and ``greeting``'s, access
the cursor object, and print the column names with the following code:

.. literalinclude:: ../../example/greetings_cursor.py
   :language: python

Accessing prepared SQL as a string
----------------------------------

When you need to do something not directly supported by aiosql, this is your
escape hatch.
You can still define your SQL in a file and load it with aiosql, but then you
may choose to use it without calling your aiosql method.
The prepared SQL string of a method is available as an attribute of each method
``queries.<method_name>.sql``.
Here's an example of how you might use it with a unique feature of ``psycopg2`` like
`execute_values <https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values>`__.

.. literalinclude:: ../../example/pg_execute_values.py
   :language: python

Accessing the SQL Operation Type
--------------------------------

Query functions also provide access to the SQL operation type you define in
your library.
This can be useful for observability (such as metrics, tracing, or logging), or
customizing how you manage different operations within your codebase. Extending
from the above example:

.. literalinclude:: ../../example/observe_query.py
   :language: python
