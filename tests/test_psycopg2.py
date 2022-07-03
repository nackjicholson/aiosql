from datetime import date

import aiosql
import psycopg2
import psycopg2.extras

import pytest
import run_tests as t


def test_version():
    assert psycopg2.__version__.startswith("2.")


@pytest.fixture()
def queries():
    return t.queries("psycopg2")


def test_record_query(pg_dsn, queries):
    with psycopg2.connect(dsn=pg_dsn, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(pg_conn, queries):
    t.run_parameterized_query(pg_conn, queries)


def test_parameterized_record_query(pg_dsn, queries):
    with psycopg2.connect(dsn=pg_dsn, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        t.run_parameterized_record_query(conn, queries, "pg", date)


def test_record_class_query(pg_conn, queries):
    t.run_record_class_query(pg_conn, queries, date)


def test_select_cursor_context_manager(pg_conn, queries):
    t.run_select_cursor_context_manager(pg_conn, queries, date)


def test_select_one(pg_conn, queries):
    t.run_select_one(pg_conn, queries)


def test_select_value(pg_conn, queries):
    t.run_select_value(pg_conn, queries)


def test_modulo(pg_conn, queries):
    actual = queries.blogs.pg_get_modulo(pg_conn, left=7, right=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(pg_conn, queries):
    t.run_insert_returning(pg_conn, queries, "pg", date)


def test_delete(pg_conn, queries):
    t.run_delete(pg_conn, queries)


def test_insert_many(pg_conn, queries):
    with pg_conn:
        t.run_insert_many(pg_conn, queries, date)


def test_execute_script(pg_conn, queries):
    with pg_conn:
        actual = queries.comments.pg_create_comments_table(pg_conn)
        assert actual == "CREATE TABLE"
