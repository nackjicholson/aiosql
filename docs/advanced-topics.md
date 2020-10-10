# Advanced Topics

## Leveraging Driver Specific Features

Todo

## Access the `cursor` object

The cursor is a temporary object created in memory that allows you to perform row-by-row operations on your data and use handy methods such as `.description`, `.fetchall()` and `.fetchone()`. As long as you are running a SQL `SELECT` query, you can access the cursor object by appending `_cursor` to the end of the queries name. For example, say you have the following query named `get-all-greetings` in a `sql` file:

```sql
-- greetings.sql

-- name: get-all-greetings
-- Get all the greetings in the database
SELECT
    greeting_id,
    greeting
FROM greetings;
```

With this query, you can get all `greeting_id`'s and `greeting`'s, access the cursor object, and print the column names with the following code:
```python
import asyncio
import aiosql
import aiosqlite
import os
from typing import List

SQL_FILE = os.path.abspath('greetings.sql')
DB_FILE = os.path.abspath('greetings.db')
queries = aiosql.from_path(SQL_FILE, "aiosqlite")


def getColNames(cursor_description: List) -> List[str]:
    """return a tables column names."""
    return [col_info[0] for col_info in cursor_description]

async def accessCursor():
    async with aiosqlite.connect(DB_FILE) as conn:
        # append _cursor after query name
        async with queries.get_all_greetings_cursor(conn) as cur:
            print(getColNames(cur.description)) # list of column names
            first_row = await cur.fetchone() 
            all_data = await cur.fetchall()
            print(f"ALL DATA: {all_data}") # tuple of first row data
            print(f"FIRST ROW: {first_row}") # list of tuples 


asyncio.run(accessCursor())
# [greeting_id, greeting]
# ALL DATA: [(1, hi), (2, aloha), (3, hola)]
# FIRST ROW: (1, hi)
```

## Accessing prepared SQL as a string

When you need to do something not directly supported by aiosql, this is your escape hatch. You can still define your sql in a file and load it with aiosql, but then you may choose to use it without calling your aiosql method. The prepared SQL string of a method is available as an attribute of each method `queries.<method_name>.sql`. Here's an example of how you might use it with a unique feature of `psycopg2` like [`execute_values`](https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values).

This example adapts the example usage from psycopg2's documentation for [`execute_values`](https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values).

```python
>>> import aiosql
>>> import psycopg2
>>> from psycopg2.extras import execute_values
>>> sql_str = """
... -- name: create_schema#
... create table test (id int primary key, v1 int, v2 int);
... 
... -- name: insert!
... INSERT INTO test (id, v1, v2) VALUES %s;
...
... -- name: update!
... UPDATE test SET v1 = data.v1 FROM (VALUES %s) AS data (id, v1)
... WHERE test.id = data.id;
...
... -- name: getem
... select * from test order by id;
... """
>>>
>>> queries = aiosql.from_str(sql_str, "psycopg2")
>>> conn = psycopg2.connect("dbname=test user=postgres")
>>> queries.create_schema(conn)
>>>
>>> cur = conn.cursor()
>>> execute_values(cur, queries.insert.sql, [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
>>> execute_values(cur, queries.update.sql, [(1, 20), (4, 50)])
>>> 
>>> queries.getem(conn)
[(1, 20, 3), (4, 50, 6), (7, 8, 9)])
```

## Sync & Async

Below are two example of a program which can print `"{greeting}, {world_name}!"` from data held in a minimal SQLite database containing greetings and worlds. They use this same sql.

_greetings.sql_

```sql
-- name: get-all-greetings
-- Get all the greetings in the database
select greeting_id,
       greeting
  from greetings;

-- name: get-worlds-by-name^
-- Get the world record from the database.
select world_id,
       world_name
  from worlds
 where world_name = :world_name;
```

Notice there is a usage of the [`^` Select One Query Operator](./defining-sql-queries.md#select-one). Adding this to the SQL comment `--name: get-world-by-name^` indicates to aiosql that `queries.get_world_by_name()` will return a single row back.

### Sync with sqlite3

Here we've set up our `sqlite3` connection. Using the `sqlite3.Row` type for our records to make it easy to access values by column names rather than as tuple indices. The program works, it does two queries sqequentially then loops over their results to print greetings.

```python
import sqlite3
import aiosql

queries = aiosql.from_path("greetings.sql", driver_adapter="sqlite3")

conn = sqlite3.connect("greetings.db")
conn.row_factory = sqlite3.Row

# greetings = [
#     <Row greeting_id=1, greeting="Hi">,
#     <Row greeting_id=2, greeting="Aloha">,
#     <Row greeting_id=3, greeting="Hola">
# ]
greetings = queries.get_all_greetings(conn)

# world = <Row world_id=1, world_name="Earth">
world = queries.get_worlds_by_name(conn, world_name="Earth")

# Hi, Earth!
# Aloha, Earth!
# Hola, Earth!
for greeting_row in greetings:
    print(f"{greeting_row['greeting']}, {world['world_name']}!")

conn.close()
```

### Asyncio with aiosqlite

This program is only a little bit different. It let's us leverage [`asyncio.gather`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) to make both queries for greetings and worlds in parallel!

```python
import asyncio

import aiosql
import aiosqlite


queries = aiosql.from_path("greetings.sql", driver_adapter="aiosqlite")

async def main():
    with async aiosqlite.connect("greetings.db") as conn:
        conn.row_factory = aiosqlite.Row
        # Parallel queries!!!
        #
        # greetings = [
        #     <Row greeting_id=1, greeting="Hi">,
        #     <Row greeting_id=2, greeting="Aloha">,
        #     <Row greeting_id=3, greeting="Hola">
        # ]
        # world = <Row world_id=1, world_name="Earth">
        greeting_rows, world = await asyncio.gather(
            queries.get_all_greetings(conn),
            queries.get_worlds_by_name(conn, world_name="Earth")
        )

        # Hi, Earth!
        # Aloha, Earth!
        # Hola, Earth!
        for greeting_row in greeting_rows:
            print(f"{greeting_row['greeting']}, {world['world_name']}!")


asyncio.run(main())
```

Slightly different usage with [aiosqlite](https://github.com/omnilib/aiosqlite) but I hope this has demonstrated in a small way the big power and performance possibilities with asyncronous queries using the async driver types.

## Type Hinting Queries with Protocols

Todo
