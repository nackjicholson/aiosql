from pathlib import Path
from typing import NamedTuple, Iterable
from datetime import date
import dataclasses
import asyncio
import re
import pytest

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
    "apsycopg": "postgres",
    "psycopg2": "postgres",
    "asyncpg": "postgres",
    "pygresql": "postgres",
    "pg8000": "postgres",
    "pymysql": "mysql",
    "pymssql": "mssql",
    "mysql-connector": "mysql",
    "mysqldb": "mysql",
    "mariadb": "mariadb",
    "duckdb": "duckdb",
}

# map databases to SQL subdirectories
_DIR = {
    "sqlite3": "li",
    "duckdb": "du",
    "postgres": "pg",
    "mysql": "my",
    "mariadb": "my",
    "mssql": "ms",
}

def _insert_blogs(todate):
    return [
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

def _expect_blogs(d):
    return list(reversed([(r["title"], r["published"]) for r in d]))

def to_tuple(v):
    """Make a tuple out of a row."""
    log.debug(f"v = {v}")
    if isinstance(v, UserBlogSummary):
        return (v.title, v.published)
    elif isinstance(v, tuple):
        return v
    elif isinstance(v, list):
        return tuple(v)
    elif isinstance(v, dict):
        return tuple(v.values())
    else:
        raise Exception(f"unexpected row type: {type(v).__name__}")

class Queries:
    """Queries wrapper

    Find the best, possibly database and driver-specific function to call.
    """

    def __init__(self, driver: str, queries):
        self._driver = driver
        self._db = _DB[driver]
        self._dir = _DIR[self._db]
        self._queries = queries
        self.is_async = driver in ("asyncpg", "aiosqlite", "apsycopg")
        self.driver_adapter = queries.driver_adapter
        assert self.is_async == hasattr(queries.driver_adapter, "is_aio_driver")

    def f(self, name: str):
        """Return the most precise SQL function for name."""
        if "." in name:
            dname, fname = name.split(".", 1)
            dname = dname + "."
        else:
            dname, fname = "", name
        names = [ f"{dname}{self._dir}.{self._driver}.{fname}", f"{dname}{self._dir}.{fname}", name ]
        for n in names:
            if n in self._queries.available_queries:
                o = self._queries
                for a in n.split("."):
                    o = getattr(o, a)
                return o
        raise Exception(f"query function not found: {name}")

@pytest.fixture(scope="module")
def queries(driver: str):
    """Load queries into AioSQL, plus a convenient test wrapper."""
    RECORD_CLASSES = {"UserBlogSummary": UserBlogSummary}
    dir_path = Path(__file__).parent / "blogdb" / "sql"
    queries = aiosql.from_path(dir_path, driver, RECORD_CLASSES, attribute="_dot_", kwargs_only=False)
    # log.warning(f"queries: {queries}")
    return Queries(driver, queries)

# actual tests use these fixtures:
#
# driver: current driver
# conn: a connection to the database
# dconn: a connection to the database which returns dicts
# date: date conversion

def run_sanity(conn):
    """Run a very little something on a connection without a schema."""
    curs = conn.cursor()
    curs.execute("SELECT 1 as one")
    res = curs.fetchone()
    assert res == (1,) or res == [1] or res == {"one": 1}
    curs.close()
    conn.commit()

def run_something(conn):
    """Run something on a connection without a schema."""

    def sel12(cur):
        cur.execute("SELECT 1 AS id, 'Calvin' AS data UNION SELECT 2, 'Susie' ORDER BY 1")
        res = [ to_tuple(r) for r in cur.fetchall() ]
        assert res == [(1, "Calvin"), (2, "Susie")] or \
               res == [{"id": 1, "data": "Calvin"}, {"id": 2, "data": "Susie"}]

    cur = conn.cursor()
    sel12(cur)
    cur.close()

    if hasattr(cur, "__enter__"):  # WITH
        with conn.cursor() as cur:
            sel12(cur)

    conn.commit()

def run_cursor(conn, queries):
    cur = queries.driver_adapter._cursor(conn)
    cur.execute("SELECT 'Hello World!' AS msg")
    res = cur.fetchone()
    assert res in [("Hello World!",), ["Hello World!"], {"msg": "Hello World!"} ]
    cur.close()
    conn.commit()

def run_record_query(dconn, queries):
    get_all = queries.f("users.get_all")
    raw_actual = get_all(dconn)
    assert isinstance(raw_actual, Iterable)
    actual = list(raw_actual)
    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }

def run_parameterized_query(conn, queries):
    # select on a parameter
    get_by_lastname = queries.f("users.get_by_lastname")
    actual = get_by_lastname(conn, lastname="Doe")
    actual = [to_tuple(r) for r in actual]
    expected = [(3, "janedoe", "Jane", "Doe"), (2, "johndoe", "John", "Doe")]
    assert actual == expected

    # select with 3 parameters
    # FIXME broken with pg8000
    # actual = queries.misc.comma_nospace_var(conn, one=1, two=10, three=100)
    # assert actual == (1, 10, 100) or actual == [1, 10, 100]
    # NOTE some drivers return a list instead of a tuple
    # FIXME broken for pymsql with as_dict, so skip
    if queries._driver != "pymssql":
        comma_nospace_var = queries.f("misc.comma_nospace_var")
        actual = to_tuple(comma_nospace_var(conn, one="Hello", two=" ", three="World!"))
        assert actual == ("Hello", " ", "World!")

    conn.commit()

def run_parameterized_record_query(dconn, queries, date):
    get_blogs_published_after = queries.f("blogs.get_blogs_published_after")

    raw_actual = get_blogs_published_after(dconn, published=date(2018, 1, 1))
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

    dconn.commit()

def run_record_class_query(conn, queries, date):
    get_user_blogs = queries.f("blogs.get_user_blogs")
    raw_actual = get_user_blogs(conn, userid=1)
    assert isinstance(raw_actual, Iterable)
    actual = list(raw_actual)

    expected = [
        UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=date(2017, 7, 28)),
    ]
    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    get_latest_user_blog = queries.f("blogs.get_latest_user_blog")
    one = get_latest_user_blog(conn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23))

    conn.commit()


def run_select_cursor_context_manager(conn, queries, date):
    fun = queries.f("blogs.get_user_blogs_cursor")
    expected = [
        ("How to make a pie.", date(2018, 11, 23)),
        ("What I did Today", date(2017, 7, 28)),
    ]

    with fun(conn, userid=1) as cursor:
        # reconversions for mysqldb and pg8000
        actual = [to_tuple(r) for r in cursor.fetchall()]
        assert actual == expected


def run_select_one(conn, queries):
    get_by_username = queries.f("users.get_by_username")
    actual = to_tuple(get_by_username(conn, username="johndoe"))
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


def run_insert_returning(conn, queries, date):
    driver = queries._driver

    publish_blog = queries.f("blogs.publish_blog")

    if driver == "duckdb":
        blogid = publish_blog(
            conn,
            2,
            "My first blog",
            "Hello, World!",
            date(2018, 12, 4),
        )
    else:
        blogid = publish_blog(
            conn,
            userid=2,
            title="My first blog",
            content="Hello, World!",
            published=date(2018, 12, 4),
        )

    # sqlite returns a number while pg query returns a tuple
    if isinstance(blogid, tuple):
        assert driver in ("psycopg", "psycopg2", "pygresql", "mariadb", "duckdb")
        blogid, title = blogid
    elif isinstance(blogid, list):
        assert driver == "pg8000"
        blogid, title = blogid
    # duckdb will return a tuple or a dict depending on how the sql is structured.
    # If you wrap the returning in `()` a dict is returned.
    elif isinstance(blogid, dict):
        assert driver in ("duckdb", "pymssql")
        title = blogid.get("title")
        blogid = blogid.get("blogid")
    else:
        assert driver in ("sqlite3", "apsw")
        blogid, title = blogid, "My first blog"

    blog_title = queries.f("blogs.blog_title")
    b2, t2 = to_tuple(blog_title(conn, blogid=blogid))
    assert (blogid, title) == (b2, t2)

    if driver in ("psycopg", "psycopg2", "apsycopg"):
        no_publish = queries.f("blogs.no_publish")
        res = no_publish(conn)
        assert res is None


def run_delete(conn, queries, expect=1):
    """Remove the "janedoe" blog entitled 'Testing'."""
    remove_blog = queries.f("blogs.remove_blog")
    get_user_blogs = queries.f("blogs.get_user_blogs")

    actual = remove_blog(conn, blogid=2)
    raw_janes_blogs = get_user_blogs(conn, userid=3)
    assert actual in (expect, -1)
    assert isinstance(raw_janes_blogs, Iterable)

    janes_blogs = list(raw_janes_blogs)
    assert len(janes_blogs) == 0


def run_insert_many(conn, queries, date, expect=3):

    blogs_dict = _insert_blogs(date)
    if queries._db in ("sqlite3", "duckdb", "mysql", "mariadb", "mssql"):
        blogs = [ to_tuple(r) for r in blogs_dict ]
    else:
        blogs = blogs_dict

    bulk_publish = queries.f("blogs.bulk_publish")
    actual = bulk_publish(conn, blogs)
    assert actual in (expect, -1)

    # check
    get_user_blogs = queries.f("blogs.get_user_blogs")
    raw_johns_blogs = get_user_blogs(conn, userid=2)
    johns_blogs = [ to_tuple(r) for r in raw_johns_blogs ]

    expected = _expect_blogs(blogs_dict)

    assert johns_blogs == expected


def run_select_value(conn, queries, expect=3):
    # test $
    get_count = queries.f("users.get_count")
    actual = get_count(conn)
    assert actual == expect

    # FIXME does not work for mysql/mariadb
    if queries._dir != "my":
        # also with quote escapes
        escape_quotes = queries.f("misc.escape_quotes")
        actual = escape_quotes(conn)
        # actual = "L'art du rire"
        assert actual == "L'art du rire"

    # pg-specific check
    if queries._db == "postgres":
        simple = queries.f("misc.escape_simple_quotes")
        actual = simple(conn)
        assert actual == "'doubled' single quotes"

    # empty result
    empty = queries.f("misc.empty")
    none = empty(conn)
    assert none is None

    conn.commit()


def run_date_time(conn, queries):
    get_now_date_time = queries.f("misc.get_now_date_time")
    now = get_now_date_time(conn)
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", now)
    conn.commit()


@dataclasses.dataclass
class Person:
    name: str
    age: int


def run_object_attributes(conn, queries):
    # success
    calvin = Person(name="Calvin", age=6)
    person_attributes = queries.f("misc.person_attributes")
    r = person_attributes(conn, p=calvin)
    if isinstance(r, (tuple, list)):
        name, age = r
        assert name == calvin.name and age == calvin.age
    elif isinstance(r, dict):
        assert r["name"] == calvin.name and r["age"] == calvin.age
    else:
        pytest.fail("unexpected query output")

    # failures
    try:
        person_attributes(conn, q=calvin)
        pytest.fail("should fail on missing parameter p")
    except ValueError as e:
        assert "missing named parameter p" in str(e)
    del calvin.age
    try:
        person_attributes(conn, p=calvin)
        pytest.fail("should fail on missing attribute age")
    except ValueError as e:
        assert "parameter p is missing attribute age" in str(e)

    conn.commit()

def run_execute_script(conn, queries):
    create_table = queries.f("comments.create_table")
    actual = create_table(conn)
    assert actual in ("DONE", "CREATE TABLE")
    conn.commit()

def run_modulo(conn, queries):
    get_modulo = queries.f("misc.get_modulo")
    actual = get_modulo(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected
    conn.commit()

#
# Asynchronous tests
#

# TODO

@pytest.mark.asyncio
async def run_async_sanity(aconn, queries):
    """Run a very little something on a connection without a schema."""
    res = await queries.driver_adapter.select_one(aconn, "testing", "SELECT 1 AS one", ())
    assert res == (1,) or res == [1] or res == {"one": 1}
    # FIXME asyncpg does not have commit() on connection
    # await conn.commit()

@pytest.mark.asyncio
async def run_async_record_query(dconn, queries):

    get_all = queries.f("users.get_all")

    actual = [dict(r) async for r in get_all(dconn)]

    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }

@pytest.mark.asyncio
async def run_async_parameterized_query(aconn, queries, date):

    get_user_blogs = queries.f("blogs.get_user_blogs")

    actual = [ row async for row in get_user_blogs(aconn, userid=1) ]
    expected = [
        ("How to make a pie.", date(2018, 11, 23)),
        ("What I did Today", date(2017, 7, 28)),
    ]
    assert actual == expected

@pytest.mark.asyncio
async def run_async_parameterized_record_query(dconn, queries, date):
    get_blogs_published_after = queries.f("blogs.get_blogs_published_after")

    records = get_blogs_published_after(dconn, published=date(2018, 1, 1))
    actual = [ dict(rec) async for rec in records ]

    expected = [
        {
            "title": "How to make a pie.",
            "username": "bobsmith",
            "published": "2018-11-23 00:00",
        },
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected

@pytest.mark.asyncio
async def run_async_record_class_query(aconn, queries, date):

    get_user_blogs = queries.f("blogs.get_user_blogs")

    actual = [ row async for row in get_user_blogs(aconn, userid=1) ]

    expected = [
        UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=date(2017, 7, 28)),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    get_latest_user_blog = queries.f("blogs.get_latest_user_blog")
    one = await get_latest_user_blog(aconn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23))

@pytest.mark.asyncio
async def run_async_select_cursor_context_manager(aconn, queries, date):
    get_user_blogs_cursor = queries.f("blogs.get_user_blogs_cursor")
    async with get_user_blogs_cursor(aconn, userid=1) as cursor:
        actual = [tuple(rec) async for rec in cursor]
        expected = [
            ("How to make a pie.", date(2018, 11, 23)),
            ("What I did Today", date(2017, 7, 28)),
        ]
        assert actual == expected

@pytest.mark.asyncio
async def run_async_select_one(aconn, queries):
    get_by_username = queries.f("users.get_by_username")
    actual = await get_by_username(aconn, username="johndoe")
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected

@pytest.mark.asyncio
async def run_async_select_value(aconn, queries):
    get_count = queries.f("users.get_count")
    actual = await get_count(aconn)
    expected = 3
    assert actual == expected

@pytest.mark.asyncio
async def run_async_insert_returning(aconn, queries, date):
    publish_blog = queries.f("blogs.publish_blog")
    blog_title = queries.f("blogs.blog_title")

    blogid = await publish_blog(
        aconn,
        userid=2,
        title="My first blog",
        content="Hello, World!",
        published=date(2018, 12, 4),
    )

    if queries._db == "postgres":
        # assert isinstance(blogid, (tuple, list))
        blogid, title = blogid
    else:
        blogid, title = blogid, "My first blog"

    actual = await blog_title(aconn, blogid=blogid)
    assert actual == (blogid, title)

@pytest.mark.asyncio
async def run_async_delete(aconn, queries):
    # Removing the "janedoe" blog titled "Testing"
    remove_blog = queries.f("blogs.remove_blog")

    actual = await remove_blog(aconn, blogid=2)
    # FIXME all implementations should return the same!
    assert actual in (1, "DELETE 1")

    get_user_blogs = queries.f("blogs.get_user_blogs")
    janes_blogs = [ r async for r in get_user_blogs(aconn, userid=3) ]
    assert len(janes_blogs) == 0

@pytest.mark.asyncio
async def run_async_insert_many(aconn, queries, date):

    bulk_publish = queries.f("blogs.bulk_publish")

    blogs_dict = _insert_blogs(date)
    if queries._db in ("sqlite3", "duckdb"):
        blogs = [ to_tuple(r) for r in blogs_dict ]
    else:
        blogs = blogs_dict

    actual = await bulk_publish(aconn, blogs)
    assert actual is None

    get_user_blogs = queries.f("blogs.get_user_blogs")
    raw_johns_blogs = get_user_blogs(aconn, userid=2)
    johns_blogs = [ tuple(r) async for r in raw_johns_blogs ]
    assert johns_blogs == _expect_blogs(blogs_dict)

@pytest.mark.asyncio
async def run_async_methods(dconn, queries):
    get_all = queries.f("users.get_all")
    get_all_sorted = queries.f("users.get_all_sorted")

    users = get_all(dconn)
    sorted_users = get_all_sorted(dconn)

    assert [dict(u) async for u in users] == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
    ]
    assert [dict(u) async for u in sorted_users] == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
    ]

@pytest.mark.asyncio
async def run_async_execute_script(aconn, queries):
    create_table = queries.f("comments.create_table")
    actual = await create_table(aconn)
    assert actual in ("DONE", "CREATE TABLE")
