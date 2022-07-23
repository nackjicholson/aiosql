from datetime import date

import aiosql
import pgdb  # PyGreSQL DB-API driver
import pytest
import run_tests as t


@pytest.fixture()
def queries():
    return t.queries("pygresql")


@pytest.fixture()
def conn(pg_params):
    dbname = pg_params["dbname"]
    del pg_params["dbname"]
    pg_params["database"] = dbname
    if "port" in pg_params:
        port = pg_params["port"]
        del pg_params["port"]
        pg_params["host"] += f":{port}"
    t.log.debug(f"params: {pg_params}")
    with pgdb.connect(**pg_params) as conn:
        yield conn


@pytest.mark.skip("row factory is not supported")
def test_record_query(pg_params, queries):
    with pgdb.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


@pytest.mark.skip("row factory is not supported")
def test_parameterized_record_query(pg_params, queries):
    with pgdb.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_parameterized_record_query(conn, queries, "pg", date)


def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, date)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, date)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries)


def test_modulo(conn, queries):
    actual = queries.blogs.pg_get_modulo(conn, left=7, right=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, "pygresql", date)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    t.run_insert_many(conn, queries, date)
