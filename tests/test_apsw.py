import aiosql
import pytest
import run_tests as t

try:
    import apsw as db
except ModuleNotFoundError:
    pytest.skip("missing driver: apsw", allow_module_level=True)

DRIVER = "apsw"

pytestmark = [
    pytest.mark.sqlite3,
]


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.fixture
def queries():
    return t.queries(DRIVER)


class APSWConnection(db.Connection):
    """APSW Connection wrapper with autocommit off."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._begin()

    def _begin(self):
        self.cursor().execute("BEGIN").close()

    def commit(self):  # pragma: no cover
        self.cursor().execute("COMMIT").close()
        self._begin()

    def _rollback(self):
        self.cursor().execute("ROLLBACK").close()

    def rollback(self):  # pragma: no cover
        self._rollback()
        self._begin()

    def close(self):
        self._rollback()
        super().close()


@pytest.fixture
def conn(sqlite3_db_path):
    conn = APSWConnection(sqlite3_db_path)
    yield conn
    conn.close()


def test_cursor(conn, queries):
    t.run_cursor(conn, queries)


def test_record_query(conn, queries):
    conn.setrowtrace(dict_factory)
    t.run_record_query(conn, queries)


def test_parameterized_query(conn, queries):
    t.run_parameterized_query(conn, queries)


def test_parameterized_record_query(conn, queries):
    conn.setrowtrace(dict_factory)
    t.run_parameterized_record_query(conn, queries, "apsw", t.todate)


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


@pytest.mark.skip("APSW does not support RETURNING?")
def test_insert_returning(conn, queries):  # pragma: no cover
    t.run_insert_returning(conn, queries, DRIVER, t.todate)


def test_delete(conn, queries):
    t.run_delete(conn, queries, expect=-1)


def test_insert_many(conn, queries):
    with conn:
        t.run_insert_many(conn, queries, t.todate, expect=-1)


def test_date_time(conn, queries):
    t.run_date_time(conn, queries, DRIVER)


def test_execute_script(conn, queries):
    with conn:
        actual = queries.comments.sqlite_create_comments_table(conn)
        assert actual == "DONE"
