# aiosql - Simple SQL in Python

SQL is code. Write it, version control it, comment it, and run it using files. Writing your SQL code in Python programs as strings doesn't allow you to easily reuse them in SQL GUIs or CLI tools like psql. With aiosql you can organize your SQL statements in _.sql_ files, load them into your python application as methods to call without losing the ability to use them as you would any other SQL file.

This project supports standard and [asyncio](https://docs.python.org/3/library/asyncio.html) based drivers for SQLite and PostgreSQL out of the box ([sqlite3](https://docs.python.org/3/library/sqlite3.html), [aiosqlite](https://aiosqlite.omnilib.dev/en/latest/?badge=latest), [psycopg2](https://www.psycopg.org/docs/), [asyncpg](https://magicstack.github.io/asyncpg/current/)). Extensions to support other database drivers can be written by you! See: [Database Driver Adapters](./database-driver-adapters.md)

!!! danger
    
    This project supports [asyncio](https://docs.python.org/3/library/asyncio.html) based drivers and requires python versions >3.6.

## Installation

```sh
pip install aiosql
```

Or if you you use [poetry](https://python-poetry.org):

```sh
poetry add aiosql
```

## Usage

_greetings.sql_

```sql
-- name: get_all_greetings
-- Get all the greetings in the database
select greeting_id, greeting from greetings;

-- name: get_user_by_username^
-- Get a user from the database
select user_id,
       username,
       name
  from users
 where username = :username;
```

_example.py_

```python
import asyncio
import aiosql
import aiosqlite


queries = aiosql.from_path("./greetings.sql", "aiosqlite")


async def main():
    # Parallel queries!!!
    async with aiosqlite.connect("greetings.db") as conn:
        greetings, user = await asyncio.gather(
            queries.get_all_greetings(conn),
            queries.get_user_by_username(conn, username="willvaughn")
        )
        # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
        # user = (1, "willvaughn", "William")

        for _, greeting in greetings:
            print(f"{greeting}, {user[2]}!")
        # Hi, William!
        # Aloha, William!
        # Hola, William!

asyncio.run(main())
```

This example has an imaginary SQLite database with greetings and users. It prints greetings in various languages to the user and showcases the basic feature of being able to load queries from a sql file and call them by name in python code. It also happens to do two SQL queries in parallel using `aiosqlite` and asyncio.
