import aiosql
import psycopg2
from psycopg2.extras import execute_values

SQL = """
-- name: create_schema#
create table if not exists test (id int primary key, v1 int, v2 int);

-- name: insert!
INSERT INTO test (id, v1, v2) VALUES %s;

-- name: update!
UPDATE test SET v1 = data.v1 FROM (VALUES %s) AS data (id, v1)
WHERE test.id = data.id;

-- name: getem
select * from test order by id;
"""

queries = aiosql.from_str(SQL, "psycopg2")
conn = psycopg2.connect("dbname=test")
queries.create_schema(conn)
with conn.cursor() as cur:
    execute_values(cur, queries.insert.sql, [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
    execute_values(cur, queries.update.sql, [(1, 20), (4, 50)])

print(list(queries.getem(conn)))
#  [(1, 20, 3), (4, 50, 6), (7, 8, 9)]
