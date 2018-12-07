# aiosql

Simple SQL in Python.

SQL is code, you should be able to write it, version control it, comment on it, and use it in database tools
like `psql` as you would any other SQL. But, you also want to be able to use it from your python
applications, and that's where `aiosql` can help. With `aiosql` you can organize your SQL statements in `.sql`
files and load them into a python object as methods to call.

This project supports sync and asyncio based drivers for SQLite (`sqlite3`, `aiosqlite`) and PostgreSQL
(`psycopg2`, `asyncpg`) out of the box, and can be extended to support other database drivers by you! The ``asyncio``
support restricts this package to python versions >3.6. If you are using older versions of python please see the
related [anosql](https://github.com/honza/anosql) package which this project is based on.

## Install

```
pip install aiosql
```

Or if you you use [poetry](https://poetry.eustace.io/):

```
poetry add aiosql
```

## Documentation

Project and API docs https://nackjicholson.github.io/aiosql
