from datetime import date

import aiosql
import pytest
import run_tests as t

try:
    import MySQLdb as db
except ModuleNotFoundError:
    pytest.skip("missing driver: MySQLdb (mysqlclient)", allow_module_level=True)

pytestmark = [
    pytest.mark.skipif(not t.has_cmd("mysqld"), reason="no mysqld"),
    pytest.mark.skipif(not t.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]

DRIVER = "mysqldb"


@pytest.fixture()
def queries():
    return t.queries(DRIVER)


# is pytest-mysql running as expected?
def test_proc(mysql_proc):
    assert mysql_proc.running()


def test_query(mysql):
    t.run_something(mysql)


def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn


def test_my_db(my_db):
    t.run_something(my_db)


# FIXME
@pytest.mark.skip("cannot connect obscure issue")
def test_record_query(my_dsn, queries):  # pragma: no cover
    with db.connect(**my_dsn) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(my_db, queries):
    t.run_parameterized_query(my_db, queries)
    my_db.commit()  # or fails on teardown


@pytest.mark.skip("cannot connect obscure issue")
def test_parameterized_record_query(my_dsn, queries):  # pragma: no cover
    with db.connect(**my_dsn) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


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


@pytest.mark.skip("mysql does not support RETURNING, but mariadb yes")
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
