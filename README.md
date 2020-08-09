# aiosql

Simple SQL in Python

SQL is code, you should be able to write it, version control it, comment it, and run it using files. Writing your SQL code in Python programs as strings doesn't allow you to easily reuse your SQL in database GUI tools or CLI tools like psql. With aiosql you can organize your SQL statements in _.sql_ files, load them into your python application as methods to call without losing the ability to use them as you would any other SQL file.

This project supports standard and [asyncio](https://docs.python.org/3/library/asyncio.html) based drivers for SQLite and PostgreSQL out of the box ([sqlite3](https://docs.python.org/3/library/sqlite3.html), [aiosqlite](https://aiosqlite.omnilib.dev/en/latest/?badge=latest), [psycopg2](https://www.psycopg.org/docs/), [asyncpg](https://magicstack.github.io/asyncpg/current/)). Extensions to support other database drivers can be written by you!

If you are using python versions <3.6 please see the related [anosql](https://github.com/honza/anosql) package which this project is based on.

## Documentation

Project and API docs https://nackjicholson.github.io/aiosql

## Install

```
pip install aiosql
```

Or if you you use [poetry](https://python-poetry.org):

```
poetry add aiosql
```

## Usage

Given you have a SQL file like the one below called `users.sql`

```sql
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
```

You can use `aiosql` to load the queries in this file for use in your Python application:

```python
import aiosql
import sqlite3

conn = sqlite3.connect("myapp.db")
queries = aiosql.from_path("users.sql", "sqlite3")

users = queries.get_all_users(conn)
# >>> [(1, "nackjicholson", "William", "Vaughn"), (2, "johndoe", "John", "Doe"), ...]

users = queries.get_user_by_username(conn, username="nackjicholson")
# >>> (1, "nackjicholson", "William", "Vaughn")
```

Writing SQL in a file and executing it from methods in python!

## Why you might want to use this

- You think SQL is pretty good, and writing SQL is an important part of your applications.
- You don't want to write your SQL in strings intermixed with your python code.
- You're not using an ORM like SQLAlchemy or Django, and you don't need to.
- You want to be able to reuse your SQL in other contexts. Loading it into psql or other database tools.

## Why you might _NOT_ want to use this

- You're looking for an ORM.
- You aren't comfortable writing SQL code.
- You don't have anything in your application that requires complicated SQL beyond basic CRUD operations.
- Dynamically loaded objects built at runtime really bother you.
