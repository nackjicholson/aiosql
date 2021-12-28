import aiosql

import pytest
import run_tests as t


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.fixture()
def queries():
    return t.queries("sqlite3")


def test_record_query(sqlite3_conn, queries):
    sqlite3_conn.row_factory = dict_factory
    t.run_record_query(sqlite3_conn, queries)


def test_parameterized_query(sqlite3_conn, queries):
    t.run_parameterized_query(sqlite3_conn, queries)


def test_parameterized_record_query(sqlite3_conn, queries):
    sqlite3_conn.row_factory = dict_factory
    t.run_parameterized_record_query(sqlite3_conn, queries, "sqlite", t.todate)


def test_record_class_query(sqlite3_conn, queries):
    t.run_record_class_query(sqlite3_conn, queries, t.todate)


def test_select_cursor_context_manager(sqlite3_conn, queries):
    t.run_select_cursor_context_manager(sqlite3_conn, queries, t.todate)


def test_select_one(sqlite3_conn, queries):
    t.run_select_one(sqlite3_conn, queries)


def test_select_value(sqlite3_conn, queries):
    t.run_select_value(sqlite3_conn, queries)


def test_modulo(sqlite3_conn, queries):
    actual = queries.blogs.sqlite_get_modulo(sqlite3_conn, left=7, right=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(sqlite3_conn, queries):
    t.run_insert_returning(sqlite3_conn, queries, "sqlite", t.todate)


def test_delete(sqlite3_conn, queries):
    t.run_delete(sqlite3_conn, queries)


def test_insert_many(sqlite3_conn, queries):
    with sqlite3_conn:
        t.run_insert_many(sqlite3_conn, queries, t.todate)


def test_execute_script(sqlite3_conn, queries):
    with sqlite3_conn:
        actual = queries.comments.sqlite_create_comments_table(sqlite3_conn)
        assert actual == "DONE"
