from datetime import date

import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import mariadb as db
except ModuleNotFoundError:
    pytest.skip("missing driver: mariadb", allow_module_level=True)

pytestmark = [
    pytest.mark.mariadb,
    pytest.mark.skipif(not u.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]

DRIVER = "mariadb"


@pytest.fixture()
def queries():
    return t.queries(DRIVER)


def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn
    assert "dbname" not in my_dsn and "database" in my_dsn


def test_query(my_conn):
    t.run_something(my_conn)


def test_my_db(my_db):
    t.run_something(my_db)


@pytest.mark.skip("FIXME users table not found?")
def test_record_query(my_conn, queries):
    t.run_record_query(my_conn, queries)


def test_parameterized_query(my_db, queries):
    t.run_parameterized_query(my_db, queries)


@pytest.mark.skip("FIXME users table not found?")
def test_parameterized_record_query(my_db, queries):
    t.run_parameterized_record_query(my_db, queries, DRIVER, date)


def test_record_class_query(my_db, queries):
    t.run_record_class_query(my_db, queries, date)
    my_db.commit()  # or fail on teardown


def test_select_cursor_context_manager(my_db, queries):
    t.run_select_cursor_context_manager(my_db, queries, date)
    my_db.commit()  # or fail on teardown


def test_select_one(my_db, queries):
    t.run_select_one(my_db, queries)
    my_db.commit()  # or fail on teardown


def test_select_value(my_db, queries):
    t.run_select_value(my_db, queries)
    my_db.commit()  # or fail on teardown


def test_insert_returning(my_db, queries):  # pragma: no cover
    t.run_insert_returning(my_db, queries, DRIVER, date)
    my_db.commit()  # or fail on teardown


def test_delete(my_db, queries):
    t.run_delete(my_db, queries)
    my_db.commit()  # or fails on teardown


def test_insert_many(my_db, queries):
    t.run_insert_many(my_db, queries, date)
    my_db.commit()


def test_date_time(my_db, queries):
    t.run_date_time(my_db, queries, DRIVER)
    my_db.commit()
