# non portable SQL statements to create, fill and clear the database schema

import asyncio
from pathlib import Path
import csv
import utils
import datetime

#
# yuk… hide sync/async
#
# We do not want to replicate schema creation functions for async.
#
# I believe that the asynchronous approach is a poor performance kludge
# against bad interpreter parallelism support (JavaScript, CPython).
# Because the interpreter is so bad at switching between contexts, the model
# just offloads the task to the user for a limited benefit as it only really
# brings improvements to IO-bound loads.
# This interpreter-level implementation induces significant code complexity and
# execution overheads.
# It makes no sense from the hardware and operating system point of view,
# which already have pretty efficient threads running on multicore cpus.

def execute_any(conn, queries, name):
    utils.log.debug(f"executing: {name}")
    f = queries.f(name)
    if queries.is_async:
        return utils.run_async(f(conn))
    else:
        return f(conn)

def execute_commit(conn, queries):
    if queries.is_async:
        # transaction management is different with asyncpg…
        if queries._driver == "asyncpg":
            return
        return utils.run_async(conn.commit())
    else:
        return conn.commit()

def execute_many(conn, queries, name, data):
    f = queries.f(name)
    if queries.is_async:
        return utils.run_async(f(conn, data))
    else:
        return f(conn, data)

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"

# schema creation
_CREATE_USER_BLOGS = [
    "blogs.create_table_users",
    "blogs.create_table_blogs",
]

def create_user_blogs(conn, queries):
    for q in _CREATE_USER_BLOGS:
        execute_any(conn, queries, q)
    execute_commit(conn, queries)
    # sanity check!
    count = execute_any(conn, queries, "users.get_count")
    assert count == 0

# schema data
def fill_user_blogs(conn, queries):
    with USERS_DATA_PATH.open() as fp:
        users = [ tuple(r) for r in csv.reader(fp) ]
        if queries._driver in ("pg8000", "asyncpg"):
            users = [ { "name": t[0], "fname": t[1], "lname": t[2] } for t in users ]
        execute_many(conn, queries, "users.add_many_users", users)
    with BLOGS_DATA_PATH.open() as fp:
        blogs = [ tuple(r) for r in csv.reader(fp) ]
        if queries._driver in ("pg8000", "asyncpg"):
            blogs = [ { "userid": int(t[0]), "title": t[1], "content": t[2], "published": datetime.date.fromisoformat(t[3]) }
                      for t in blogs ]
        execute_many(conn, queries, "blogs.add_many_blogs", blogs)
    execute_commit(conn, queries)

# schema destruction
_DROP_USER_BLOGS = [
    "blogs.drop_table_comments",
    "blogs.drop_table_blogs",
    "blogs.drop_table_users",
]

def drop_user_blogs(conn, queries):
    for q in _DROP_USER_BLOGS:
        execute_any(conn, queries, q)
    execute_commit(conn, queries)
