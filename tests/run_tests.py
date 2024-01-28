from pathlib import Path
from typing import NamedTuple, Iterable
from datetime import date
import asyncio
import re

import aiosql
from utils import log


# for sqlite3
def todate(year, month, day):
    return f"{year:04}-{month:02}-{day:02}"


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
    "mariadb": "mariadb",
    "duckdb": "duckdb",
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


def run_cursor(conn, queries):
    cur = queries.driver_adapter._cursor(conn)
    cur.execute("SELECT 'Hello World!'")
    res = cur.fetchone()
    assert res in [("Hello World!",), ["Hello World!"]]
    cur.close()


def run_record_query(conn, queries):
    raw_actual = queries.users.get_all(conn)
    assert isinstance(raw_actual, Iterable)
    actual = list(raw_actual)
    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


def run_parameterized_query(conn, queries, db=None):
    # select on a parameter
    actual = queries.users.get_by_lastname(conn, lastname="Doe")
    expected = [(3, "janedoe", "Jane", "Doe"), (2, "johndoe", "John", "Doe")]
    # NOTE re-conversion needed for mysqldb and pg8000
    actual = [tuple(i) for i in actual]
    assert actual == expected

    # select with 3 parameters
    # FIXME broken with pg8000
    # actual = queries.misc.comma_nospace_var(conn, one=1, two=10, three=100)
    # assert actual == (1, 10, 100) or actual == [1, 10, 100]
    actual = queries.misc.comma_nospace_var(conn, one="Hello", two=" ", three="World!")

    # NOTE some drivers return a list instead of a tuple
    assert actual == ("Hello", " ", "World!") or actual == ["Hello", " ", "World!"]


def run_parameterized_record_query(conn, queries, db, todate):
    if _DB[db] == "sqlite3":
        fun = queries.blogs.sqlite_get_blogs_published_after
    elif _DB[db] == "duckdb":
        fun = queries.blogs.duckdb_get_blogs_published_after
    elif _DB[db] == "postgres":
        fun = queries.blogs.pg_get_blogs_published_after
    elif _DB[db] in ("mysql", "mariadb"):
        fun = queries.blogs.my_get_blogs_published_after
    else:
        raise Exception(f"unexpected driver: {db}")

    raw_actual = fun(conn, published=todate(2018, 1, 1))
    assert isinstance(raw_actual, Iterable)
    actual = list(raw_actual)

    expected = [
        {
            "title": "How to make a pie.",
            "username": "bobsmith",
            "published": "2018-11-23 00:00",
        },
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


def run_record_class_query(conn, queries, todate, db=None):
    raw_actual = queries.blogs.get_user_blogs(conn, userid=1)
    assert isinstance(raw_actual, Iterable)
    actual = list(raw_actual)

    expected = [
        UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=todate(2017, 7, 28)),
    ]
    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    one = queries.blogs.get_latest_user_blog(conn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=todate(2018, 11, 23))


def run_select_cursor_context_manager(conn, queries, todate, db=None):
    fun = queries.blogs.get_user_blogs_cursor
    expected = [
        ("How to make a pie.", todate(2018, 11, 23)),
        ("What I did Today", todate(2017, 7, 28)),
    ]

    with fun(conn, userid=1) as cursor:
        # reconversions for mysqldb and pg8000
        actual = [tuple(r) for r in cursor.fetchall()]
        assert actual == expected


def run_select_one(conn, queries, db=None):
    actual = queries.users.get_by_username(conn, username="johndoe")

    # reconversion for pg8000
    actual = tuple(actual)
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


def run_insert_returning(conn, queries, db, todate):
    if _DB[db] in ("sqlite3"):
        fun = queries.blogs.publish_blog
    elif _DB[db] in ("duckdb"):
        fun = queries.blogs.duckdb_publish_blog
    elif _DB[db] in ("postgres", "mariadb"):
        fun = queries.blogs.pg_publish_blog
    elif _DB[db] == "mysql":
        fun = queries.blogs.my_publish_blog
    else:
        raise Exception(f"unexpected driver: {db}")

    if db == "duckdb":
        blogid = fun(
            conn,
            2,
            "My first blog",
            "Hello, World!",
            todate(2018, 12, 4),
        )
    else:
        blogid = fun(
            conn,
            userid=2,
            title="My first blog",
            contents="Hello, World!",
            published=todate(2018, 12, 4),
        )

    # sqlite returns a number while pg query returns a tuple
    if isinstance(blogid, tuple):
        assert db in ("psycopg", "psycopg2", "pygresql", "mariadb", "duckdb")
        blogid, title = blogid
    elif isinstance(blogid, list):
        assert db == "pg8000"
        blogid, title = blogid
    # duckdb will return a tuple or a dict depending on how the sql is structured.
    # If you wrap the returning in `()` a dict is returned.
    elif isinstance(blogid, dict):
        assert db == "duckdb"
        title = blogid.get("title")
        blogid = blogid.get("blogid")
    else:
        assert db in ("sqlite3", "apsw")
        blogid, title = blogid, "My first blog"

    b2, t2 = queries.blogs.blog_title(conn, blogid=blogid)
    assert (blogid, title) == (b2, t2)

    if db and db in ("psycopg", "psycopg2"):
        res = queries.blogs.pg_no_publish(conn)
        assert res is None


def run_delete(conn, queries, expect=1, db=None):
    # Removing the "janedoe" blog titled "Testing"
    actual = queries.blogs.remove_blog(conn, blogid=2)
    raw_janes_blogs = queries.blogs.get_user_blogs(conn, userid=3)
    assert actual in (expect, -1)
    assert isinstance(raw_janes_blogs, Iterable)

    janes_blogs = list(raw_janes_blogs)
    assert len(janes_blogs) == 0


def run_insert_many(conn, queries, todate, expect=3, db=None):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "contents": "content - 1",
            "published": todate(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "contents": "content - 2",
            "published": todate(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "contents": "content - 3",
            "published": todate(2018, 12, 6),
        },
    ]

    actual = queries.blogs.pg_bulk_publish(conn, blogs)
    raw_johns_blogs = queries.blogs.get_user_blogs(conn, userid=2)
    expected = [
        ("Blog Part 3", todate(2018, 12, 6)),
        ("Blog Part 2", todate(2018, 12, 5)),
        ("Blog Part 1", todate(2018, 12, 4)),
    ]

    assert actual in (expect, -1)
    johns_blogs = [tuple(r) for r in raw_johns_blogs]
    assert johns_blogs == expected


def run_select_value(conn, queries, db, expect=3):
    # test $
    actual = queries.users.get_count(conn)
    assert actual == expect
    # also with quote escapes
    if _DB[db] in ("mysql", "mariadb"):
        # FIXME does not work
        # actual = queries.misc.my_escape_quotes(conn)
        actual = "L'art du rire"
    else:  # pg, duckdb & sqlite
        actual = queries.misc.escape_quotes(conn)
    assert actual == "L'art du rire"
    # pg-specific check
    if _DB[db] == "postgres":
        actual = queries.misc.pg_escape_quotes(conn)
        assert actual == "'doubled' single quotes"
    # empty result
    none = queries.misc.empty(conn)
    assert none is None


def run_date_time(conn, queries, db):
    if _DB[db] == "sqlite3":
        now = queries.misc.get_now_date_time(conn)
    elif _DB[db] == "duckdb":
        now = queries.misc.duckdb_get_now_date_time(conn)
    elif _DB[db] == "postgres":
        now = queries.misc.pg_get_now_date_time(conn)
    elif _DB[db] in ("mysql", "mariadb"):
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
        else queries.blogs.sqlite_get_blogs_published_after if _DB[db] == "sqlite3" else None
    )
    records = await fun(conn, published=todate(2018, 1, 1))

    actual = [dict(rec) for rec in records]

    expected = [
        {
            "title": "How to make a pie.",
            "username": "bobsmith",
            "published": "2018-11-23 00:00",
        },
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
        contents="Hello, World!",
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
    # log.warning(f"actual = {actual}")
    # FIXME all implementations should return the same!
    assert actual == "DELETE 1" or actual == 1

    janes_blogs = await queries.blogs.get_user_blogs(conn, userid=3)
    assert len(janes_blogs) == 0


async def run_async_insert_many(conn, queries, todate):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "contents": "content - 1",
            "published": todate(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "contents": "content - 2",
            "published": todate(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "contents": "content - 3",
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
