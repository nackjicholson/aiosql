import asyncio
from pathlib import Path

import aiosql
import aiosqlite
import pytest

from conftest import UserBlogSummary


@pytest.fixture()
def queries(record_classes):
    dir_path = Path(__file__).parent / "blogdb/sql"
    return aiosql.from_path(dir_path, "aiosqlite", record_classes)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.mark.asyncio
async def test_record_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        actual = await queries.users.get_all(conn)

        assert len(actual) == 3
        assert actual[0] == {
            "userid": 1,
            "username": "bobsmith",
            "firstname": "Bob",
            "lastname": "Smith",
        }


@pytest.mark.asyncio
async def test_parameterized_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.blogs.get_user_blogs(conn, userid=1)
        expected = [("How to make a pie.", "2018-11-23"), ("What I did Today", "2017-07-28")]
        assert actual == expected


@pytest.mark.asyncio
async def test_parameterized_record_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        actual = await queries.blogs.sqlite_get_blogs_published_after(conn, published="2018-01-01")

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
async def test_record_class_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.blogs.get_user_blogs(conn, userid=1)
        expected = [
            UserBlogSummary(title="How to make a pie.", published="2018-11-23"),
            UserBlogSummary(title="What I did Today", published="2017-07-28"),
        ]

        assert all(isinstance(row, UserBlogSummary) for row in actual)
        assert actual == expected


@pytest.mark.asyncio
async def test_select_cursor_context_manager(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        async with queries.blogs.get_user_blogs_cursor(conn, userid=1) as cursor:
            actual = [row async for row in cursor]
            expected = [("How to make a pie.", "2018-11-23"), ("What I did Today", "2017-07-28")]
            assert actual == expected


@pytest.mark.asyncio
async def test_select_one(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.users.get_by_username(conn, username="johndoe")

    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


@pytest.mark.asyncio
async def test_insert_returning(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        blogid = await queries.blogs.publish_blog(
            conn, userid=2, title="My first blog", content="Hello, World!", published="2018-12-04"
        )

        sql = """
            select title
              from blogs
             where blogid = :blogid;"""
        async with conn.execute(sql, {"blogid": blogid}) as cur:
            actual = await cur.fetchone()
            expected = ("My first blog",)
            assert actual == expected


@pytest.mark.asyncio
async def test_delete(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        # Removing the "janedoe" blog titled "Testing"
        actual = await queries.blogs.remove_blog(conn, blogid=2)
        assert actual is None

        janes_blogs = await queries.blogs.get_user_blogs(conn, userid=3)
        assert len(janes_blogs) == 0


@pytest.mark.asyncio
async def test_insert_many(sqlite3_db_path, queries):
    blogs = [
        (2, "Blog Part 1", "content - 1", "2018-12-04"),
        (2, "Blog Part 2", "content - 2", "2018-12-05"),
        (2, "Blog Part 3", "content - 3", "2018-12-06"),
    ]

    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.blogs.sqlite_bulk_publish(conn, blogs)
        assert actual is None

        johns_blogs = await queries.blogs.get_user_blogs(conn, userid=2)
        assert johns_blogs == [
            ("Blog Part 3", "2018-12-06"),
            ("Blog Part 2", "2018-12-05"),
            ("Blog Part 1", "2018-12-04"),
        ]


@pytest.mark.asyncio
async def test_async_methods(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        users, sorted_users = await asyncio.gather(
            queries.users.get_all(conn), queries.users.get_all_sorted(conn)
        )

    assert users == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
    ]
    assert sorted_users == [
        {"userid": 1, "username": "bobsmith", "firstname": "Bob", "lastname": "Smith"},
        {"userid": 3, "username": "janedoe", "firstname": "Jane", "lastname": "Doe"},
        {"userid": 2, "username": "johndoe", "firstname": "John", "lastname": "Doe"},
    ]
