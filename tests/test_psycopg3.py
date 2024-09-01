import datetime
import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import psycopg as db
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    pytest.skip("missing driver: psycopg", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
]

DRIVER = "psycopg"

@pytest.fixture(scope="module")
def queries():
    return t.queries(DRIVER)

@pytest.fixture
def conn(pg_conn):
    return pg_conn

@pytest.fixture
def dconn(pg_params):
    with db.connect(**pg_params, row_factory=dict_row) as conn:
        yield conn

@pytest.fixture
def date():
    return datetime.date

from run_tests import (
    run_sanity as test_sanity,
    run_something as test_something,
    run_cursor as test_cursor,
    run_record_query as test_record_query,
    run_parameterized_record_query as test_parameterized_record_query,
    run_parameterized_query as test_parameterized_query,
    run_select_one as test_select_one,
    run_select_value as test_select_value,
    run_modulo as test_modulo,
    run_delete as test_delete,
    run_date_time as test_date_time,
    run_execute_script as test_execute_script,
    run_object_attributes as test_object_attributes,
    run_record_class_query as test_record_class_query,
    run_select_cursor_context_manager as test_select_cursor_context_manager,
    run_insert_returning as test_insert_returning,
    run_insert_many as test_insert_many,
)

def test_version():
    assert db.__version__.startswith("3.")

def test_select_value_dict(dconn, queries):
    t.run_select_value(dconn, queries)
