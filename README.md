# aiosql

Simple SQL in Python.

SQL is code, you should be able to write it, version control it, comment on it, and use it in database tools
like `psql` as you would any other SQL. But, you also want to be able to use it from your python
applications, and that's where `aiosql` can help. With `aiosql` you can organize your SQL in `.sql`
files and load them into a python object with methods to call.

The project is based on (and closely related to) the python package [anosql](https://github.com/honza/anosql), which
is based on the clojure library [Yesql](https://github.com/krisajenkins/yesql/). It supports sync and asyncio
drivers for SQLite and PostgreSQL out of the box, and can be extended by you to support other database drivers!

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
