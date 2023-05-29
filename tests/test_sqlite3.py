import aiosql
import pytest
import run_tests as t
import sqlite3 as db

pytestmark = [pytest.mark.sqlite3]

DRIVER = "sqlite3"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.fixture
def conn(sqlite3_db_path):
    conn = db.connect(sqlite3_db_path)
    yield conn
    conn.close()


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


def test_record_query(conn, queries):
    conn.row_factory = dict_factory
    t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


def test_parameterized_record_query(conn, queries):
    conn.row_factory = dict_factory
    t.run_parameterized_record_query(conn, queries, DRIVER, t.todate)


def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, t.todate)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, t.todate)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries, DRIVER)


def test_modulo(conn, queries):
    actual = queries.blogs.sqlite_get_modulo(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, DRIVER, t.todate)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    with conn:
        t.run_insert_many(conn, queries, t.todate)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, DRIVER)


def test_execute_script(conn, queries):
    with conn:
        actual = queries.comments.sqlite_create_comments_table(conn)
        assert actual == "DONE"
