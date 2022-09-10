from datetime import date

import aiosql
import pytest
import run_tests as t

try:
    import pymysql as db
except ModuleNotFoundError:
    pytest.skip("missing driver: pymysql", allow_module_level=True)

DRIVER = "pymysql"

pytestmark = [
    pytest.mark.skipif(not t.has_cmd("mysqld"), reason="no mysqld"),
    pytest.mark.skipif(not t.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]


@pytest.fixture()
def queries():
    return t.queries(DRIVER)


@pytest.fixture()
def pymysql_db_dsn(my_db, my_dsn):
    my_dsn["database"] = "test"  # FIXME hardcoded
    yield my_dsn


@pytest.fixture()
def pymysql_db(pymysql_db_dsn):
    with db.connect(**pymysql_db_dsn) as conn:
        yield conn
        conn.commit()


@pytest.fixture
def pymysql_nodb(my_dsn):
    with db.connect(**my_dsn) as conn:
        yield conn
        conn.commit()


# is pytest-mysql running as expected?
def test_proc(mysql_proc):
    assert mysql_proc.running()


def test_query_nodb(pymysql_nodb):
    t.run_something(pymysql_nodb)


def test_query_db(pymysql_db):
    t.run_something(pymysql_db)


def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn


def test_record_query(pymysql_db_dsn, queries):
    with db.connect(**pymysql_db_dsn, cursorclass=db.cursors.DictCursor) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(pymysql_db, queries):
    t.run_parameterized_query(pymysql_db, queries)


@pytest.mark.skip("pymysql issue when mogrifying because of date stuff %Y")
def test_parameterized_record_query(pymysql_db_dsn, queries):  # pragma: no cover
    with db.connect(**pymysql_db_dsn, cursorclass=db.cursors.DictCursor) as conn:
        t.run_parameterized_record_query(conn, queries, DRIVER, date)


def test_record_class_query(pymysql_db, queries):
    t.run_record_class_query(pymysql_db, queries, date)


def test_select_cursor_context_manager(pymysql_db, queries):
    t.run_select_cursor_context_manager(pymysql_db, queries, date)


def test_select_one(pymysql_db, queries):
    t.run_select_one(pymysql_db, queries)


@pytest.mark.skip("mysql does not support RETURNING, although mariadb does")
def test_insert_returning(pymysql_db, queries):  # pragma: no cover
    t.run_insert_returning(pymysql_db, queries, DRIVER, date)


def test_delete(pymysql_db, queries):
    t.run_delete(pymysql_db, queries)


def test_insert_many(pymysql_db, queries):
    t.run_insert_many(pymysql_db, queries, date)


def test_date_time(pymysql_db, queries):
    t.run_date_time(pymysql_db, queries, DRIVER)
