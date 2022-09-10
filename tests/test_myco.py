from datetime import date

import aiosql
import pytest
import run_tests as t

try:
    import mysql.connector as db
except ModuleNotFoundError:
    pytest.skip("missing driver: mysql.connector (mysql-connector)", allow_module_level=True)

pytestmark = [
    pytest.mark.skipif(not t.has_cmd("mysqld"), reason="no mysqld"),
    pytest.mark.skipif(not t.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]

DRIVER = "mysql-connector"


@pytest.fixture()
def queries():
    return t.queries(DRIVER)


@pytest.fixture()
def myco_db_dsn(my_db, my_dsn):
    my_dsn["database"] = "test"  # FIXME hardcoded
    yield my_dsn


@pytest.fixture()
def myco_db(myco_db_dsn):
    conn = db.connect(**myco_db_dsn)
    yield conn
    conn.commit()
    conn.close()


@pytest.fixture
def myco_nodb(my_dsn):
    conn = db.connect(**my_dsn)
    yield conn
    conn.commit()
    conn.close()


# is pytest-mysql running as expected?
def test_proc(mysql_proc):
    assert mysql_proc.running()


def test_query_nodb(myco_nodb):
    t.run_something(myco_nodb)


def test_query_db(myco_db):
    t.run_something(myco_db)


def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn


@pytest.mark.skip("myco cursor handling is unclear")
def test_record_query(myco_db_dsn, queries):
    with db.connect(**myco_db_dsn, cursorclass=myco.cursors.DictCursor) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(myco_db, queries):
    t.run_parameterized_query(myco_db, queries)


@pytest.mark.skip("myco cursor handling is unclear")
def test_parameterized_record_query(myco_db_dsn, queries):  # pragma: no cover
    with db.connect(**myco_db_dsn, cursorclass=myco.cursors.DictCursor) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


def test_record_class_query(myco_db, queries):
    t.run_record_class_query(myco_db, queries, date)


def test_select_cursor_context_manager(myco_db, queries):
    t.run_select_cursor_context_manager(myco_db, queries, date)


def test_select_one(myco_db, queries):
    t.run_select_one(myco_db, queries)


@pytest.mark.skip("mysql does not support RETURNING, although mariadb does")
def test_insert_returning(myco_db, queries):  # pragma: no cover
    t.run_insert_returning(myco_db, queries, DRIVER, date)


def test_delete(myco_db, queries):
    t.run_delete(myco_db, queries)


def test_insert_many(myco_db, queries):
    t.run_insert_many(myco_db, queries, date)


def test_date_time(myco_db, queries):
    t.run_date_time(myco_db, queries, DRIVER)
