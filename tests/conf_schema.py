# non portable SQL statements to create, fill and clear the database schema

import asyncio
from pathlib import Path
import csv
import utils

# yuk… hide sync/async

def execute_any(conn, queries, name):
    utils.log.debug(f"executing: {name}")
    f = queries.f(name)
    if queries.is_async:
        return utils.run_async(f(conn))
    else:
        return f(conn)

def execute_commit(conn, queries):
    if queries.is_async:
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

# NOTE not used by postgres nor duckdb
def fill_user_blogs(conn, queries):
    with USERS_DATA_PATH.open() as fp:
        users = list(csv.reader(fp))
        execute_many(conn, queries, "users.add_many_users", users)
    with BLOGS_DATA_PATH.open() as fp:
        blogs = list(csv.reader(fp))
        execute_many(conn, queries, "blogs.add_many_blogs", blogs)
    execute_commit(conn, queries)
