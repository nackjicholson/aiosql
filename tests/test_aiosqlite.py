import aiosql
import pytest
import run_tests as t

try:
    import aiosqlite
    import pytest_asyncio
except ModuleNotFoundError as m:
    pytest.skip(f"missing module: {m}", allow_module_level=True)

pytestmark = [
    pytest.mark.sqlite3,
]

@pytest.fixture(scope="module")
def driver():
    return "aiosqlite"

@pytest.fixture(scope="module")
def date():
    return t.todate

@pytest_asyncio.fixture
async def rconn(li_dbpath):
    async with aiosqlite.connect(li_dbpath) as conn:
        yield conn

@pytest_asyncio.fixture
def aconn(li_db):
    yield li_db

@pytest_asyncio.fixture
def dconn(aconn):
    aconn.row_factory = aiosqlite.Row
    yield aconn

from run_tests import (
  run_async_sanity as test_sanity,
  run_async_record_query as test_record_query,
  run_async_parameterized_record_query as test_parameterized_record_query,
  run_async_parameterized_query as test_parameterized_query,
  run_async_record_class_query as test_record_class_query,
  run_async_select_one as test_record_select_one,
  run_async_select_value as test_record_select_value,
  run_async_insert_returning as test_record_insert_returning,
  run_async_delete as test_delete,
  run_async_insert_many as test_insert_many,
  run_async_execute_script as test_execute_script,
  run_async_methods as test_methods,
  run_async_select_cursor_context_manager as test_select_cursor_context_manager,
)
