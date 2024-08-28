import aiosql
import pytest
import run_tests as t
import utils as u
from datetime import date

try:
    import duckdb as db
except ModuleNotFoundError:
    pytest.skip("missing driver: duckdb", allow_module_level=True)

pytestmark = [pytest.mark.duckdb]

DRIVER = "duckdb"


@pytest.fixture
def conn(duckdb_conn):
    return duckdb_conn


@pytest.fixture
def queries():
    return t.queries(DRIVER)


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


@pytest.mark.skip("does not work yet")
def test_record_query(conn, queries):
    queries.driver_adapter.convert_row_to_dict = True
    t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


@pytest.mark.skip("does not work yet")
def test_parameterized_record_query(conn, queries):
    # queries.driver_adapter.convert_row_to_dict = True
    t.run_parameterized_record_query(conn, queries, date)


@pytest.mark.skip("does not work yet")
def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, date)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, date)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries)


def test_modulo(conn, queries):
    t.run_modulo(conn, queries)


def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, t.todate)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    t.run_insert_many(conn, queries, date)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries)


def test_execute_script(conn, queries):
    t.run_execute_script(conn, queries)
