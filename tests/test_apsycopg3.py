import datetime
import aiosql
import pytest
import pytest_asyncio
import run_tests as t
import utils as u
import copy

try:
    import psycopg as db
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    pytest.skip("missing driver: psycopg", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
    pytest.mark.skipif(not u.has_pkg("pytest_asyncio"), reason="no pytest_asyncio"),
]

@pytest.fixture(scope="module")
def driver():
    return "apsycopg"

@pytest.fixture(scope="module")
def date():
    return datetime.date

# FIXME merge?

# raw connection without database data
@pytest_asyncio.fixture
async def rconn(pg_params):
    conn = await db.AsyncConnection.connect(**pg_params)
    yield conn
    await conn.close()

# asynchronous tuple connection with database data
@pytest_asyncio.fixture
async def aconn(rconn, pg_db):
    yield rconn

# asynchronous dict connection with database data
@pytest_asyncio.fixture
async def dconn(pg_params, pg_db):
    params = copy.copy(pg_params)
    params["row_factory"] = dict_row
    conn = await db.AsyncConnection.connect(**params)
    yield conn
    await conn.close()

from run_tests import (
    run_async_sanity as test_sanity,
    run_async_record_query as test_record_query,
    run_async_parameterized_record_query as test_parameterized_record_query,
    run_async_parameterized_query as test_parameterized_query,
    run_async_select_one as test_select_one,
    run_async_select_value as test_select_value,
    run_async_delete as test_delete,
    run_async_execute_script as test_execute_script,
    run_async_record_class_query as test_record_class_query,
    run_async_methods as test_methods,
    run_async_select_cursor_context_manager as test_select_cursor_context_manager,
    run_async_insert_returning as test_insert_returning,
    run_async_insert_many as test_insert_many,
)

def test_version():
    assert db.__version__.startswith("3.")
