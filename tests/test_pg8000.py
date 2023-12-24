from datetime import date
import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import pg8000 as db
except ModuleNotFoundError:
    pytest.skip("missing driver: pg8000", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
]

DRIVER = "pg8000"


@pytest.fixture
def queries():
    return t.queries(DRIVER)


@pytest.fixture
def conn(pg_params):
    dbname = pg_params["dbname"]
    del pg_params["dbname"]
    pg_params["database"] = dbname
    # cleanup unsupported keyword arguments
    for kw in ("sslcertmode", "connect_timeout", "hostaddr"):
        if kw in pg_params:
            del pg_params[kw]
    u.log.debug(f"params: {pg_params}")
    with db.connect(**pg_params) as conn:
        yield conn


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


@pytest.mark.skip("row factory is not supported")
def test_record_query(pg_params, queries):
    with db.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


@pytest.mark.skip("row factory is not supported")
def test_parameterized_record_query(pg_params, queries):
    with db.connect(**pg_params, row_factory=dict_row) as conn:
        t.run_parameterized_record_query(conn, queries, "pg", date)


def test_record_class_query(conn, queries):
    t.run_record_class_query(conn, queries, date)


def test_select_cursor_context_manager(conn, queries):
    t.run_select_cursor_context_manager(conn, queries, date)


def test_select_one(conn, queries):
    t.run_select_one(conn, queries)


def test_select_value(conn, queries):
    t.run_select_value(conn, queries, DRIVER)


def test_modulo(conn, queries):
    actual = queries.blogs.pg_get_modulo_2(conn, numerator=7, denominator=3)
    expected = 7 % 3
    assert actual == expected


def test_insert_returning(conn, queries):
    t.run_insert_returning(conn, queries, DRIVER, date)


def test_delete(conn, queries):
    t.run_delete(conn, queries)


def test_insert_many(conn, queries):
    t.run_insert_many(conn, queries, date)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, DRIVER)


# @pytest.mark.skip("not supported")
def test_execute_script(conn, queries):
    actual = queries.comments.pg_create_comments_table(conn)
    assert actual == "DONE"
