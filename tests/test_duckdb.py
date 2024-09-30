import datetime
import aiosql
import pytest

try:
    import duckdb as db
except ModuleNotFoundError:
    pytest.skip("missing driver: duckdb", allow_module_level=True)

pytestmark = [pytest.mark.duckdb]

@pytest.fixture(scope="module")
def driver():
    return "duckdb"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest.fixture
def conn(duckdb_conn):
    return duckdb_conn

# FIXME dconn

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
    # KO
	# run_record_query as test_record_query,
	# run_parameterized_record_query as test_parameterized_record_query,
	# run_record_class_query as test_record_class_query,
	run_parameterized_query as test_parameterized_query,
	run_select_cursor_context_manager as test_select_cursor_context_manager,
	run_select_one as test_select_one,
	run_insert_returning as test_insert_returning,
	run_delete as test_delete,
	run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
	run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
	run_modulo as test_modulo,
)

def test_no_cursor(conn):
    adapter = aiosql.adapters.duckdb.DuckDBAdapter(use_cursor=False)
    cursor = adapter._cursor(conn)
    assert cursor == conn
