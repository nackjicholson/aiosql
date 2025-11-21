import datetime
import pytest
import aiosql
import run_tests as t
import utils as u

try:
    import asyncpg
    import pytest_asyncio
except ModuleNotFoundError as m:
    pytest.skip(f"missing module: {m}", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    # pytest.mark.asyncio,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
    pytest.mark.skipif(not u.has_pkg("pytest_asyncio"), reason="no pytest_asyncio"),
]

@pytest.fixture(scope="module")
def driver():
    return "asyncpg"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest_asyncio.fixture
async def rconn(pg_dsn):
    conn = await asyncpg.connect(pg_dsn)
    yield conn
    await conn.close()

@pytest_asyncio.fixture
async def aconn(pg_db):
    yield pg_db

@pytest_asyncio.fixture
async def dconn(aconn):
    # FIXME dict row?
    yield aconn

from run_tests import (
    run_async_sanity as test_async_sanity,
    run_async_record_query as test_async_record_query,
    run_async_parameterized_query as test_async_parameterized_query,
    run_async_parameterized_record_query as test_async_parameterized_record_query,
    run_async_record_class_query as test_async_record_class_query,
    run_async_select_cursor_context_manager as test_async_select_cursor_context_manager,
    run_async_select_one as test_async_select_one,
    run_async_select_value as test_async_select_value,
    run_async_insert_returning as test_async_insert_returning,
    run_async_delete as test_async_delete,
    run_async_insert_many as test_async_insert_many,
    run_async_execute_script as test_async_execute_script,
)

# TODO other pools?
@pytest.mark.asyncio
async def test_with_pool(pg_dsn, queries, pg_db):
    async with asyncpg.create_pool(pg_dsn) as pool:
        async with pool.acquire() as conn:
            await t.run_async_insert_returning(conn, queries, datetime.date)

@pytest.mark.asyncio
async def test_async_methods(pg_dsn, queries, pg_db):
    async with asyncpg.create_pool(pg_dsn) as pool:
        await t.run_async_methods(pool, queries)

@pytest.mark.asyncio
async def test_no_publish(aconn, queries):
    # TODO move in run
    no_publish = queries.f("blogs.no_publish")
    res = await no_publish(aconn)
    assert res is None

def test_many_replacements(pg_dsn, queries):
    """If the replacement was longer than the variable, bad SQL was generated.

    The variable replacement code had a bug that caused it to miscalculate where in the
    original string to put the placeholders.  The SQL below would produce a query that
    ended with "$8, $9, $10$11:k);" because of this bug.

    This test would fail before the bug was fixed and passes afterward.

    This issue was reported in https://github.com/nackjicholson/aiosql/issues/90.
    """

    sql = """
      -- name: test<!
      INSERT INTO table VALUES (:a, :b, :c, :d, :e, :f, :g, :h, :i, :j, :k);
    """
    actual = aiosql.from_str(sql, "asyncpg").test.sql
    expected = "INSERT INTO table VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);"
    assert actual == expected

@pytest.mark.asyncio
async def test_variable_replacement(aconn, queries):
    # Addresses bug reported in the following github issue:
    # https://github.com/nackjicholson/aiosql/issues/51
    #
    # When the test fails the users_sql below will fail to increment the $2
    # variable for lastname.
    search = queries.f("users.search")
    users_sql = "select username from users where firstname = $1 and lastname = $2;"
    assert search.sql == users_sql

    users_res = [ row async for row in search(aconn, title="John", lastname="Doe") ]
    assert users_res == [("johndoe",)]

    square = queries.f("misc.square")
    square_sql = "select $1::int * $1::int as squared;"
    assert square.sql == square_sql

    square_res = await square(aconn, val=42)
    assert square_res == 1764

def test_maybe_order_params():
    a = aiosql.adapters.asyncpg.AsyncPGAdapter()
    try:
        a.maybe_order_params("foo", "wrong-type-parameter")
        pytest.fail("exception should be raised")  # pragma: no cover
    except ValueError as e:
        assert "dict or tuple" in str(e)
