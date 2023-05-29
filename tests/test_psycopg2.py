from datetime import date

import aiosql
import pytest
import run_tests as t
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

DRIVER = "psycopg2"


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.fixture
def conn(pg_conn):
    return pg_conn


def test_version():
    assert db.__version__.startswith("2.")


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


def test_record_query(pg_dsn, queries):
    with db.connect(dsn=pg_dsn, cursor_factory=DictCursor) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


def test_parameterized_record_query(pg_dsn, queries):
    with db.connect(dsn=pg_dsn, cursor_factory=DictCursor) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, date)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, date)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries, DRIVER)


def test_modulo(conn, queries):
    actual = queries.blogs.pg_get_modulo(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, DRIVER, date)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    t.run_insert_many(conn, queries, date)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, DRIVER)


def test_execute_script(conn, queries):
    actual = queries.comments.pg_create_comments_table(conn)
    assert actual == "CREATE TABLE"
