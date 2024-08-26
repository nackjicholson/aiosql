from datetime import date

import aiosql
import pytest
import run_tests as t
import utils as u

DB = "mssql"
DRIVER = "pymssql"

try:
    import pymssql as db  # Python MS SQL driver
except ModuleNotFoundError:
    pytest.skip(f"missing driver: {DRIVER}", allow_module_level=True)

pytestmark = [
    pytest.mark.mssql,
    pytest.mark.skipif(not u.has_pkg(DRIVER), reason=f"no {DRIVER}"),
]


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.fixture
def conn(ms_conn):
    yield ms_conn


def test_sanity(ms_master):
    with db.connect(**ms_master) as conn:
        t.run_sanity(conn)


def test_cursor(ms_db, conn, queries):
    t.run_cursor(conn, queries)


def test_record_query(ms_dsn, ms_db, queries):
    with db.connect(**ms_dsn) as conn:
        t.run_record_query(conn, queries, db=DB)


def test_parameterized_query(conn, queries, ms_db):
    t.run_parameterized_query(conn, queries, db=DB, driver=DRIVER)


def test_parameterized_record_query(ms_dsn, queries, ms_db):
    # row_factory=dict_row
    with db.connect(**ms_dsn) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


@pytest.mark.skip(reason="currently broken with is_dict")
def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, date)


def test_select_cursor_context_manager(conn, queries, ms_db):
    t.run_select_cursor_context_manager(conn, queries, date)


def test_select_one(conn, queries, ms_db):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries, DRIVER)


def test_modulo(conn, queries):
    actual = queries.blogs.sqlite_get_modulo(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(conn, queries, ms_db):
    t.run_insert_returning(conn, queries, DRIVER, date)


def test_delete(conn, queries, ms_db):
    t.run_delete(conn, queries)


@pytest.mark.skip(reason="currently broken")
def test_insert_many(conn, queries, ms_db):
    t.run_insert_many(conn, queries, date)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, DRIVER)


def test_execute_script(conn, queries, ms_db):
    actual = queries.comments.ms_create_comments_table(conn)
    assert actual == "DONE"
