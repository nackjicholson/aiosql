# non portable SQL statements to create, fill and clear the database schema

import csv
from pathlib import Path
import utils as u
import asyncio

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"

# schema creation
_CREATE_USER_BLOGS = [
    "blogs.create_table_users",
    "blogs.create_table_blogs",
]

def async_run(awaitable):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)

def create_user_blogs(conn, queries):
    run = async_run if queries.is_async else lambda x: x
    for q in _CREATE_USER_BLOGS:
        u.log.debug(f"executing: {q}")
        f = queries.f(q)
        r = run(f(conn))
    conn.commit()
    # sanity check!
    count = queries.f("users.get_count")
    assert run(count(conn)) == 0

# schema destruction
_DROP_USER_BLOGS = [
    "blogs.drop_table_comments",
    "blogs.drop_table_blogs",
    "blogs.drop_table_users",
]

def drop_user_blogs(conn, queries):
    for q in _DROP_USER_BLOGS:
        u.log.debug(f"executing: {q}")
        f = queries.f(q)
        f(conn)
    conn.commit()

# TODO improve aiosql integration
def fill_user_blogs(conn, db):
    # NOTE postgres filling relies on copy
    # NOTE duckdb filling relies on its own functions
    assert db in ("sqlite", "mysql", "mssql")
    param = "?" if db == "sqlite" else "%s"
    cur = conn.cursor()
    with USERS_DATA_PATH.open() as fp:
        users = list(csv.reader(fp))
        cur.executemany(
            f"""
               INSERT INTO users (
                    username,
                    firstname,
                    lastname
               ) VALUES ({param}, {param}, {param});""",
            users,
        )
    with BLOGS_DATA_PATH.open() as fp:
        blogs = list(csv.reader(fp))
        cur.executemany(
            f"""
                INSERT INTO blogs (
                    userid,
                    title,
                    content,
                    published
                ) VALUES ({param}, {param}, {param}, {param});""",
            blogs,
        )
    cur.close()
    conn.commit()
