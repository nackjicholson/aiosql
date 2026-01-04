AioSQL - Backlog
================

Todo or not, that is the question…

- maintain up-to-date wrt Python moving target…
- add apsw, duckdb, asyncpg and psycopg2 to pypy 3.13 when possible.
- once 3.9 support is dropped, update old-style type hints.
- write a small SQLite3-based tutorial?
- make parameters mandatory by default, optional under some option?
- tests with even more database and drivers?
- rethink record classes? we just really want a row conversion function?
- add documentation about docker runs? isn't `docker/README.md` enough?
- `HugSQL <https://www.hugsql.org/>`_ Clojure library as support for multiple
  kind of substitutions, maybe we could do the same.

  For instance for identifiers:

  .. code:: sql

      -- name: select(cols, table)
      SELECT :i*:cols FROM :i:table ORDER BY 1;

  .. code:: python

      res = db.select(conn, cols=["uid", "name"], table="users")

  This would require separating identifiers management and to build
  and memoize the query variants?
  How much help for is there from drivers?
