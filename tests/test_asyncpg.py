from datetime import date

import pytest
import aiosql
import run_tests as t
import utils as u

try:
    import asyncpg
except ModuleNotFoundError:
    pytest.skip("missing driver: asyncpg", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    # pytest.mark.asyncio,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
    pytest.mark.skipif(not u.has_pkg("pytest_asyncio"), reason="no pytest_asyncio"),
]

DRIVER = "asyncpg"


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.mark.asyncio
async def test_record_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_record_query(conn, queries)
    await conn.close()


@pytest.mark.asyncio
async def test_parameterized_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await t.run_async_parameterized_query(conn, queries, date)
    await conn.close()


@pytest.mark.asyncio
async def test_many_replacements(pg_dsn, queries):
    """If the replacement was longer than the variable, bad SQL was generated.

    The variable replacement code had a bug that caused it to miscalculate where in the
    original string to put the placeholders.  The SQL below would produce a query that
    ended with "$8, $9, $10$11:k);" because of this bug.

    This test would fail before the bug was fixed and passes afterward.

    This issue was reported in https://github.com/nackjicholson/aiosql/issues/90.
    """
    sql = r"""
        -- name: test<!
        INSERT INTO table VALUES (:a, :b, :c, :d, :e, :f, :g, :h, :i, :j, :k);
    """
    actual = aiosql.from_str(sql, "asyncpg").test.sql
    expected = "INSERT INTO table " "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);"
    assert actual == expected


@pytest.mark.asyncio
async def test_parameterized_record_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_parameterized_record_query(conn, queries, DRIVER, date)
    await conn.close()


@pytest.mark.asyncio
async def test_record_class_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_record_class_query(conn, queries, date)
    await conn.close()


@pytest.mark.asyncio
async def test_select_cursor_context_manager(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_select_cursor_context_manager(conn, queries, date)
    await conn.close()


@pytest.mark.asyncio
async def test_select_one(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_select_one(conn, queries)
    await conn.close()


@pytest.mark.asyncio
async def test_select_value(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_select_value(conn, queries)
    await conn.close()


@pytest.mark.asyncio
async def test_insert_returning(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        async with pool.acquire() as conn:
            await t.run_async_insert_returning(conn, queries, DRIVER, date)

    conn = await asyncpg.connect(pg_dsn)
    res = await queries.blogs.pg_no_publish(conn)
    assert res is None
    await conn.close()


@pytest.mark.asyncio
async def test_delete(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_delete(conn, queries)
    await conn.close()


@pytest.mark.asyncio
async def test_insert_many(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    await t.run_async_insert_many(conn, queries, date)
    await conn.close()


@pytest.mark.asyncio
async def test_async_methods(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        await t.run_async_methods(pool, queries)


@pytest.mark.asyncio
async def test_execute_script(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        actual = await queries.comments.pg_create_comments_table(pool, queries)
        assert actual == "CREATE TABLE"


@pytest.mark.asyncio
async def test_variable_replacement(pg_dsn, queries):
    # Addresses bug reported in the following github issue:
    # https://github.com/nackjicholson/aiosql/issues/51
    #
    # When the test fails the users_sql below will fail to increment the $2
    # variable for lastname.
    async with asyncpg.create_pool(pg_dsn) as pool:
        blogs_sql = "select title from blogs where title = $1 and published = $2;"
        assert queries.blogs.search.sql == blogs_sql
        users_sql = "select username from users where firstname = $1 and lastname = $2;"
        assert queries.users.search.sql == users_sql

        blogs_res = await queries.blogs.search(pool, title="Testing", published=date(2018, 1, 1))
        users_res = await queries.users.search(pool, title="John", lastname="Doe")
        assert blogs_res == [("Testing",)]
        assert users_res == [("johndoe",)]

        square_sql = "select $1::int * $1::int as squared;"
        assert queries.blogs.square.sql == square_sql

        square_res = await queries.blogs.square(pool, val=42)
        assert square_res == 1764


def test_maybe_order_params():
    a = aiosql.adapters.asyncpg.AsyncPGAdapter()
    try:
        a.maybe_order_params("foo", "wrong-type-parameter")
        assert False, "exception should be raised"  # pragma: no cover
    except ValueError as e:
        assert "dict or tuple" in str(e)
