import datetime
import aiosql
import pytest
import utils as u

try:
    import psycopg2 as db
    from psycopg2.extras import RealDictCursor as DictCursor
except ModuleNotFoundError:
    pytest.skip("missing driver: psycopg2", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
]

@pytest.fixture(scope="module")
def driver():
    return "psycopg2"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest.fixture
def rconn(pg_dsn):
    with db.connect(dsn=pg_dsn) as conn:
        yield conn

@pytest.fixture
def conn(pg_db):
    yield pg_db

@pytest.fixture
def dconn(pg_dsn, pg_db):
    with db.connect(dsn=pg_dsn, cursor_factory=DictCursor) as conn:
        yield conn

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
	run_record_query as test_record_query,
	run_parameterized_query as test_parameterized_query,
	run_parameterized_record_query as test_parameterized_record_query,
	run_record_class_query as test_record_class_query,
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

def test_version():
    assert db.__version__.startswith("2.")
