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

Project and API docs https://willvaughn.gitlab.io/aiosql

## Usage

### Basics

Given a `greetings.sql` file:

```sql
-- name: get-all-greetings
-- Get all the greetings in the database
select * from greetings;

-- name: $get-users-by-username
-- Get all the users from the database,
-- and return it as a dict
select * from users where username = :username;
```

With the stdlib `sqlite3` driver built into python you can use this sql file:

```python
import sqlite3
import aiosql

queries = aiosql.from_path("greetings.sql", db_driver="sqlite3")
conn = sqlite3.connect("greetings.db")

greetings = queries.get_greetings(conn)
users = queries.get_users_by_username(conn, username="willvaughn")
# greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
# users = [{"user_id": 1, "username": "willvaughn", "name": "Will"}]


name = users[0]["name"]
for _, greeting in greetings:
    print(f"{greeting}, {name}!")

# Hi, Will!
# Aloha, Will!
# Hola, Will!
```

To do this in an asyncio environment you can use the [aiosqlite](https://github.com/jreese/aiosqlite) driver.

```python
import asyncio

import aiosql
import aiosqlite


async def main():
    queries = aiosql.from_path("greetings.sql", db_driver="aiosqlite")

    # Parallel queries!!!
    with async aiosqlite.connect("greetings.db") as conn:
        greetings, users = await asyncio.gather(
            queries.get_all_greetings(conn),
            queries.get_users_by_username(conn, username="willvaughn")
        )
        
    name = users[0]["name"]
    for _, greeting in greetings:
        print(f"{greeting}, {name}!")
    # greetings = [(1, "Hi"), (2, "Aloha"), (3, "Hola")]
    # users = [{"user_id": 1, "username": "willvaughn", "name": "Will"}]
        
    # Hi, Will!
    # Aloha, Will!
    # Hola, Will!
    

asyncio.run(main())
```
