from pathlib import Path
from typing import NamedTuple
from datetime import date
import shutil
import asyncio
import logging
import re

import aiosql

log = logging.getLogger("test")


# for sqlite3
def todate(year, month, day):
    return f"{year:04}-{month:02}-{day:02}"


def has_cmd(cmd):
    return shutil.which(cmd) is not None


def has_pkg(pkg):
    try:
        __import__(pkg)
        return True
    except ModuleNotFoundError:
        return False


class UserBlogSummary(NamedTuple):
    title: str
    published: date


# map drivers to databases
_DB = {
    "sqlite3": "sqlite3",
    "apsw": "sqlite3",
    "aiosqlite": "sqlite3",
    "psycopg": "postgres",
    "psycopg2": "postgres",
    "asyncpg": "postgres",
    "pygresql": "postgres",
    "pg8000": "postgres",
    "pymysql": "mysql",
    "mysql-connector": "mysql",
    "mysqldb": "mysql",
}


RECORD_CLASSES = {"UserBlogSummary": UserBlogSummary}


def queries(driver):
    """Load queries into AioSQL."""
    dir_path = Path(__file__).parent / "blogdb" / "sql"
    return aiosql.from_path(dir_path, driver, RECORD_CLASSES)


def run_something(conn):
    """Run something on a connection without a schema."""

    def sel12(cur):
        cur.execute("SELECT 1, 'un' UNION SELECT 2, 'deux' ORDER BY 1")
        res = cur.fetchall()
        assert type(res) in (tuple, list), f"unexpected type: {type(res)}"
        assert res == ((1, "un"), (2, "deux")) or res == [(1, "un"), (2, "deux")]

    cur = conn.cursor()
    has_with = hasattr(cur, "__enter__")
    sel12(cur)
    cur.close()

    if has_with:  # if available
        with conn.cursor() as cur:
            sel12(cur)

    conn.commit()


def run_record_query(conn, queries):
    actual = queries.users.get_all(conn)
    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


def run_parameterized_query(conn, queries):
    actual = queries.users.get_by_lastname(conn, lastname="Doe")
    expected = [(3, "janedoe", "Jane", "Doe"), (2, "johndoe", "John", "Doe")]
    # NOTE re-conversion needed for mysqldb and pg8000
    actual = [tuple(i) for i in actual]
    assert actual == expected


def run_parameterized_record_query(conn, queries, db, todate):
    # this black-generated indentation is a joke…
    fun = (
        queries.blogs.sqlite_get_blogs_published_after
        if _DB[db] == "sqlite3"
        else queries.blogs.pg_get_blogs_published_after
        if _DB[db] == "postgres"
        else queries.blogs.my_get_blogs_published_after
        if _DB[db] == "mysql"
        else None
    )

    actual = fun(conn, published=todate(2018, 1, 1))

    expected = [
        {"title": "How to make a pie.", "username": "bobsmith", "published": "2018-11-23 00:00"},
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


def run_record_class_query(conn, queries, todate):
    actual = queries.blogs.get_user_blogs(conn, userid=1)
    expected = [
        UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=todate(2017, 7, 28)),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    one = queries.blogs.get_latest_user_blog(conn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23))


def run_select_cursor_context_manager(conn, queries, todate):
    with queries.blogs.get_user_blogs_cursor(conn, userid=1) as cursor:
        # reconversions for mysqldb and pg8000
        actual = [tuple(r) for r in cursor.fetchall()]
        expected = [
            ("How to make a pie.", todate(2018, 11, 23)),
            ("What I did Today", todate(2017, 7, 28)),
        ]
        assert actual == expected


def run_select_one(conn, queries):
    actual = queries.users.get_by_username(conn, username="johndoe")
    # reconversion for pg8000
    actual = tuple(actual)
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


def run_insert_returning(conn, queries, db, todate):
    fun = (
        queries.blogs.publish_blog
        if _DB[db] == "sqlite3"
        else queries.blogs.pg_publish_blog
        if _DB[db] == "postgres"
        else queries.blogs.my_publish_blog
        if _DB[db] == "mysql"
        else None
    )

    blogid = fun(
        conn,
        userid=2,
        title="My first blog",
        content="Hello, World!",
        published=todate(2018, 12, 4),
    )

    # sqlite returns a number while pg query returns a tuple
    if isinstance(blogid, tuple):
        assert db in ("psycopg", "psycopg2", "pygresql")
        blogid, title = blogid
    elif isinstance(blogid, list):
        assert db == "pg8000"
        blogid, title = blogid
    else:
        assert db in ("sqlite3", "apsw")
        blogid, title = blogid, "My first blog"

    b2, t2 = queries.blogs.blog_title(conn, blogid=blogid)

    assert (blogid, title) == (b2, t2)

    if db in ("psycopg", "psycopg2"):
        res = queries.blogs.pg_no_publish(conn)
        assert res is None


def run_delete(conn, queries, expect=1):
    # Removing the "janedoe" blog titled "Testing"
    actual = queries.blogs.remove_blog(conn, blogid=2)
    assert actual == expect

    janes_blogs = queries.blogs.get_user_blogs(conn, userid=3)
    assert len(janes_blogs) == 0


def run_insert_many(conn, queries, todate, expect=3):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "content": "content - 1",
            "published": todate(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "content": "content - 2",
            "published": todate(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "content": "content - 3",
            "published": todate(2018, 12, 6),
        },
    ]

    actual = queries.blogs.pg_bulk_publish(conn, blogs)
    assert actual == expect

    johns_blogs = queries.blogs.get_user_blogs(conn, userid=2)
    expected = [
        ("Blog Part 3", todate(2018, 12, 6)),
        ("Blog Part 2", todate(2018, 12, 5)),
        ("Blog Part 1", todate(2018, 12, 4)),
    ]
    johns_blogs = [tuple(r) for r in johns_blogs]
    assert johns_blogs == expected


def run_select_value(conn, queries, expect=3):
    actual = queries.users.get_count(conn)
    assert actual == expect


def run_date_time(conn, queries, db):
    if _DB[db] == "sqlite3":
        now = queries.misc.get_now_date_time(conn)
    elif _DB[db] == "postgres":
        now = queries.misc.pg_get_now_date_time(conn)
    elif _DB[db] == "mysql":
        now = queries.misc.my_get_now_date_time(conn)
    else:
        assert False, f"unexpected driver: {db}"
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", now)


#
# Asynchronous tests
#


async def run_async_record_query(conn, queries):
    actual = [dict(r) for r in await queries.users.get_all(conn)]

    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


async def run_async_parameterized_query(conn, queries, todate):
    actual = await queries.blogs.get_user_blogs(conn, userid=1)
    expected = [
        ("How to make a pie.", todate(2018, 11, 23)),
        ("What I did Today", todate(2017, 7, 28)),
    ]
    assert actual == expected


async def run_async_parameterized_record_query(conn, queries, db, todate):
    fun = (
        queries.blogs.pg_get_blogs_published_after
        if _DB[db] == "postgres"
        else queries.blogs.sqlite_get_blogs_published_after
        if _DB[db] == "sqlite3"
        else None
    )
    records = await fun(conn, published=todate(2018, 1, 1))

    actual = [dict(rec) for rec in records]

    expected = [
        {"title": "How to make a pie.", "username": "bobsmith", "published": "2018-11-23 00:00"},
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


async def run_async_record_class_query(conn, queries, todate):
    actual = await queries.blogs.get_user_blogs(conn, userid=1)

    expected = [
        UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=todate(2017, 7, 28)),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    one = await queries.blogs.get_latest_user_blog(conn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23))


async def run_async_select_cursor_context_manager(conn, queries, todate):
    async with queries.blogs.get_user_blogs_cursor(conn, userid=1) as cursor:
        actual = [tuple(rec) async for rec in cursor]
        expected = [
            ("How to make a pie.", todate(2018, 11, 23)),
            ("What I did Today", todate(2017, 7, 28)),
        ]
        assert actual == expected


async def run_async_select_one(conn, queries):
    actual = await queries.users.get_by_username(conn, username="johndoe")
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


async def run_async_select_value(conn, queries):
    actual = await queries.users.get_count(conn)
    expected = 3
    assert actual == expected


async def run_async_insert_returning(conn, queries, db, todate):

    is_pg = _DB[db] == "postgres"

    fun = queries.blogs.pg_publish_blog if is_pg else queries.blogs.publish_blog

    blogid = await fun(
        conn,
        userid=2,
        title="My first blog",
        content="Hello, World!",
        published=todate(2018, 12, 4),
    )

    if is_pg:
        blogid, title = blogid
    else:
        blogid, title = blogid, "My first blog"

    if is_pg:
        query = "select blogid, title from blogs where blogid = $1;"
        actual = tuple(
            await conn.fetchrow(
                query,
                blogid,
            )
        )
    else:
        query = "select blogid, title from blogs where blogid = :blogid;"
        async with conn.execute(query, {"blogid": blogid}) as cur:
            actual = await cur.fetchone()
    assert actual == (blogid, title)


async def run_async_delete(conn, queries):
    # Removing the "janedoe" blog titled "Testing"
    actual = await queries.blogs.remove_blog(conn, blogid=2)
    assert actual is None

    janes_blogs = await queries.blogs.get_user_blogs(conn, userid=3)
    assert len(janes_blogs) == 0


async def run_async_insert_many(conn, queries, todate):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "content": "content - 1",
            "published": todate(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "content": "content - 2",
            "published": todate(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "content": "content - 3",
            "published": todate(2018, 12, 6),
        },
    ]
    actual = await queries.blogs.pg_bulk_publish(conn, blogs)
    assert actual is None

    johns_blogs = await queries.blogs.get_user_blogs(conn, userid=2)
    assert johns_blogs == [
        ("Blog Part 3", todate(2018, 12, 6)),
        ("Blog Part 2", todate(2018, 12, 5)),
        ("Blog Part 1", todate(2018, 12, 4)),
    ]


async def run_async_methods(conn, queries):
    users, sorted_users = await asyncio.gather(
        queries.users.get_all(conn), queries.users.get_all_sorted(conn)
    )

    assert [dict(u) for u in users] == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
    ]
    assert [dict(u) for u in sorted_users] == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
    ]
