import asyncio
from datetime import date
from pathlib import Path

import aiosql
import asyncpg
import pytest

from conftest import UserBlogSummary


@pytest.fixture()
def queries(record_classes):
    dir_path = Path(__file__).parent / "blogdb/sql"
    return aiosql.from_path(dir_path, "asyncpg", record_classes)


@pytest.mark.asyncio
async def test_record_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = [dict(rec) for rec in await queries.users.get_all(conn)]
    await conn.close()

    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


@pytest.mark.asyncio
async def test_parameterized_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.blogs.get_user_blogs(conn, userid=1)
    await conn.close()

    expected = [("How to make a pie.", date(2018, 11, 23)), ("What I did Today", date(2017, 7, 28))]
    assert actual == expected


@pytest.mark.asyncio
async def test_parameterized_record_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    records = await queries.blogs.pg_get_blogs_published_after(conn, published=date(2018, 1, 1))
    actual = [dict(rec) for rec in records]
    await conn.close()

    expected = [
        {"title": "How to make a pie.", "username": "bobsmith", "published": "2018-11-23 00:00"},
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


@pytest.mark.asyncio
async def test_record_class_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.blogs.get_user_blogs(conn, userid=1)
    await conn.close()

    expected = [
        UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=date(2017, 7, 28)),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected


@pytest.mark.asyncio
async def test_select_cursor_context_manager(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    async with queries.blogs.get_user_blogs_cursor(conn, userid=1) as cursor:
        actual = [tuple(rec) async for rec in cursor]
        expected = [
            ("How to make a pie.", date(2018, 11, 23)),
            ("What I did Today", date(2017, 7, 28)),
        ]
        assert actual == expected
    await conn.close()


@pytest.mark.asyncio
async def test_select_one(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.users.get_by_username(conn, username="johndoe")
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


@pytest.mark.asyncio
async def test_insert_returning(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        blogid, title = await queries.blogs.pg_publish_blog(
            pool,
            userid=2,
            title="My first blog",
            content="Hello, World!",
            published=date(2018, 12, 4),
        )
        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """\
                select blogid,
                       title
                  from blogs
                 where blogid = $1;
                """,
                blogid,
            )
            expected = tuple(record)

    assert (blogid, title) == expected


@pytest.mark.asyncio
async def test_delete(pg_dsn, queries):
    # Removing the "janedoe" blog titled "Testing"
    conn = await asyncpg.connect(pg_dsn)

    actual = await queries.blogs.remove_blog(conn, blogid=2)
    assert actual is None

    janes_blogs = await queries.blogs.get_user_blogs(conn, userid=3)
    assert len(janes_blogs) == 0

    await conn.close()


@pytest.mark.asyncio
async def test_insert_many(pg_dsn, queries):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "content": "content - 1",
            "published": date(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "content": "content - 2",
            "published": date(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "content": "content - 3",
            "published": date(2018, 12, 6),
        },
    ]
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.blogs.pg_bulk_publish(conn, blogs)
    assert actual is None

    johns_blogs = await queries.blogs.get_user_blogs(conn, userid=2)
    assert johns_blogs == [
        ("Blog Part 3", date(2018, 12, 6)),
        ("Blog Part 2", date(2018, 12, 5)),
        ("Blog Part 1", date(2018, 12, 4)),
    ]
    await conn.close()


@pytest.mark.asyncio
async def test_async_methods(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        users, sorted_users = await asyncio.gather(
            queries.users.get_all(pool), queries.users.get_all_sorted(pool)
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
