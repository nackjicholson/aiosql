from datetime import date

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


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.fixture
def conn(pg_conn):
    return pg_conn


def test_version():
    assert db.__version__.startswith("3.")


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


def test_record_query(pg_params, queries):
    with db.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_record_query(conn, queries)
        # test select_value with dict_row
        t.run_select_value(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


def test_parameterized_record_query(pg_params, queries):
    with db.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_parameterized_record_query(conn, queries, date)


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
    t.run_insert_returning(conn, queries, date)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    t.run_insert_many(conn, queries, date)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries)


def test_execute_script(conn, queries):
    t.run_execute_script(conn, queries)


def test_object_attributes(conn, queries):
    t.run_object_attributes(conn, queries)
