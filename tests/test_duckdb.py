import aiosql
import pytest
from aiosql.queries import Queries
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
def queries() -> Queries:
    return t.queries(DRIVER)


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


@pytest.mark.skip("does not work yet")
def test_record_query(conn, queries: Queries):
    queries.driver_adapter.convert_row_to_dict = True
    t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries, DRIVER)


@pytest.mark.skip("does not work yet")
def test_parameterized_record_query(conn, queries):
    # queries.driver_adapter.convert_row_to_dict = True
    t.run_parameterized_record_query(conn, queries, DRIVER, date)


@pytest.mark.skip("does not work yet")
def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, t.todate, DRIVER)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, date, DRIVER)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries, DRIVER)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries, db=DRIVER)


def test_modulo(conn, queries):
    actual = queries.blogs.sqlite_get_modulo(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected


@pytest.mark.skip("does not work anymore, on version 0.9.0")
def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, db=DRIVER, todate=t.todate)


def test_delete(conn, queries):
    t.run_delete(conn, queries, db=DRIVER)


@pytest.mark.skip("does not work yet: execute many does not support named parameters?")
def test_insert_many(conn, queries):
    with conn:
        t.run_insert_many(conn, queries, t.todate, db=DRIVER)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, db=DRIVER)


def test_execute_script(conn, queries):
    with conn:
        actual = queries.comments.duckdb_create_comments_table(conn)
        assert actual == "DONE"
