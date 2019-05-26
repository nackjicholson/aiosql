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

## Getting Started

#### Basic Usage

Given you have a SQL file like the one below called `users.sql`

```sql
-- name: get-all-users
-- Get all user records
select * from users;


-- name: get-user-by-username
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
# >>> [(1, "nackjicholson", "William", "Vaughn")
```

This is pretty nice, we're able to define our methods in SQL and use them as methods from python!

#### Query Operators to define different types of SQL actions

`aiosql` can help you do even more by allowing you to declare in the SQL how you would like a query to be executed
and returned in python. For instance, the `get-user-by-username` query above should really only return a single result
instead of a list containing one user. With the raw `sqlite3` driver in python we would probably have used 
`cur.fetchone()` instead of `cur.fetchall()` to retrieve a single row. We can inform `aiosql` to select a single row
by using the `^` (select one) operator on the end of our query name.

```sql
-- name: get-user-by-username^
-- Get user with the given username field.
select userid,
       username,
       firstname,
       lastname
  from users
 where username = :username;
```

```python
nack = queries.get_user_by_username(conn, username="nackjicholson")
# >>> (1, "nackjicholson", "William", "Vaughn")
```

#### Using your own python types for SQL data.

By declaring a `record_class` directive in our SQL file we can inform `aiosql` to automatically marshal our data to a
custom class we've defined in python. In python3.7 a good choice for this is the new `dataclass` package.

```sql
-- name: get-user-by-username^
-- record_class: User
-- Get user with the given username field.
select userid,
       username,
       firstname,
       lastname
  from users
 where username = :username;
```

All we have to do is provide our custom type to `aiosql` when we load our queries via the `record_classes` argument.

```python
import aiosql
import sqlite3
from dataclasses import dataclass


@dataclass
class User:
    userid: int
    username: str
    firstname: str
    lastname: str


conn = sqlite3.connect("myapp.db")
queries = aiosql.from_path("users.sql", "sqlite3", record_classes={"User": User})

nack = queries.get_user_by_username(conn, username="nackjicholson")
# >>> User(userid=1, username="nackjicholson", firstname="William", lastname="Vaughn")
```

Hopefully this is enough to intrigue you and entice you to give aiosql a try. Check the documentation site for more
information, and more features. Happy SQLing!

## Documentation

Project and API docs https://nackjicholson.github.io/aiosql
