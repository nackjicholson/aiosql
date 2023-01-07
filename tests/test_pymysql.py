from datetime import date

import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import pymysql as db
except ModuleNotFoundError:
    pytest.skip("missing driver: pymysql", allow_module_level=True)

DRIVER = "pymysql"

pytestmark = [
    pytest.mark.mysql,
    pytest.mark.skipif(not u.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]


@pytest.fixture()
def queries():
    return t.queries(DRIVER)


def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn


def test_my_conn(my_conn):
    assert my_conn.__module__.startswith(db.__name__)
    t.run_something(my_conn)


def test_my_db(my_db):
    assert my_db.__module__.startswith(db.__name__)
    t.run_something(my_db)


def test_record_query(my_db, my_dsn, queries):
    with db.connect(**my_dsn, cursorclass=db.cursors.DictCursor) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(my_db, my_dsn, queries):
    t.run_parameterized_query(my_db, queries)


@pytest.mark.skip("pymysql issue when mogrifying because of date stuff %Y")
def test_parameterized_record_query(my_db, my_dsn, queries):  # pragma: no cover
    with db.connect(**pymysql_db_dsn, cursorclass=db.cursors.DictCursor) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


def test_record_class_query(my_db, queries):
    t.run_record_class_query(my_db, queries, date)


def test_select_cursor_context_manager(my_db, queries):
    t.run_select_cursor_context_manager(my_db, queries, date)


def test_select_one(my_db, queries):
    t.run_select_one(my_db, queries)


def test_select_value(my_db, queries):
    t.run_select_value(my_db, queries, DRIVER)


@pytest.mark.skip("MySQL does not support RETURNING")
def test_insert_returning(my_db, queries):  # pragma: no cover
    t.run_insert_returning(my_db, queries, DRIVER, date)


def test_delete(my_db, queries):
    t.run_delete(my_db, queries)


def test_insert_many(my_db, queries):
    t.run_insert_many(my_db, queries, date)


def test_date_time(my_db, queries):
    t.run_date_time(my_db, queries, DRIVER)
