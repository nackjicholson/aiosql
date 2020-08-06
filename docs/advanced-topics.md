# Advanced Topics

## Leveraging Driver Specific Features

## Access the `cursor` object

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

## Type Hinting Queries with Protocols
