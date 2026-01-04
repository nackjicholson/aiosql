import sys
import re
import inspect
from pathlib import Path
from unittest import mock

import aiosql
from aiosql import SQLParseException, SQLLoadException
from aiosql.queries import Queries
from aiosql.query_loader import QueryLoader

import pytest

pytestmark = [
    pytest.mark.misc,
]


@pytest.fixture
def sql_dir():
    return Path(__file__).parent / "blogdb/sql"


@pytest.fixture
def sql_file(sql_dir):
    return sql_dir / "blogs/blogs.sql"


@pytest.fixture
def sql(sql_file):
    with open(sql_file) as f:
        return f.read()


def test_version():
    assert re.match(r"\d+\.\d+(\.?dev\d*)?$", aiosql.__version__)


def test_frompath_queries_cls(sql_dir):
    class TestQueries(Queries):
        pass

    queries = aiosql.from_path(sql_dir, "aiosqlite", queries_cls=TestQueries, kwargs_only=False)
    assert isinstance(queries, TestQueries)

    assert repr(queries).startswith("Queries(")


def test_frompath_queryloader_cls(sql_dir):
    mock_loader = mock.MagicMock(wraps=QueryLoader)

    aiosql.from_path(sql_dir, "aiosqlite", loader_cls=mock_loader, kwargs_only=False)

    assert mock_loader.called


def test_fromstr_queries_cls(sql):
    class TestQueries(Queries):
        pass

    queries = aiosql.from_str(sql, "aiosqlite", queries_cls=TestQueries)
    assert isinstance(queries, TestQueries)


def test_fromstr_queryloader_cls(sql):
    mock_loader = mock.MagicMock(wraps=QueryLoader)

    aiosql.from_str(sql, "aiosqlite", loader_cls=mock_loader)

    assert mock_loader.called


def test_trailing_space_on_lines_does_not_error():
    # There is whitespace in this string after the line ends
    sql_str = "-- name: trailing-space    ()    ^    \n"
    sql_str += "select * from test;     \n"

    try:
        aiosql.from_str(sql_str, "aiosqlite")
    except SQLParseException:  # pragma: no cover
        pytest.fail("Raised SQLParseException due to trailing space in query.")


def test_non_ascii_char():
    # this triggers a warning, that we do not really check but for coverage
    q = aiosql.from_str("-- name: zéro()\nSELECT 0;\n", "sqlite3")
    assert "zéro" in q._available_queries
    q = aiosql.from_str("-- name: éêèëÉÊÈË()\nSELECT 'eeeeeeee!';\n", "sqlite3")
    assert "éêèëÉÊÈË" in q._available_queries
    q = aiosql.from_str("-- name: 안녕하세요()\nSELECT 'hello!';\n", "sqlite3")
    assert "안녕하세요" in q._available_queries


def test_loading_query_signature():
    sql_str = "-- name: get(foo, bar)^\n" "select * from test where foo=:foo and bar=:bar"
    queries = aiosql.from_str(sql_str, "aiosqlite")
    assert queries.get.__signature__ == inspect.Signature(
        [
            inspect.Parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
            inspect.Parameter("foo", kind=inspect.Parameter.KEYWORD_ONLY),
            inspect.Parameter("bar", kind=inspect.Parameter.KEYWORD_ONLY),
        ]
    )


def test_names():
    try:
        queries = aiosql.from_str("-- name: 1st()\nSELECT 1;\n", "sqlite3")
        pytest.fail("'1st' should be rejected")
    except SQLParseException as e:
        assert '"1st()"' in str(e)
    try:
        queries = aiosql.from_str("-- name: one()$garbage\nSELECT 1;\n", "sqlite3")
        pytest.fail("garbage should be rejected")
    except SQLParseException as e:
        assert 'garbage"' in str(e)
    try:
        queries = aiosql.from_str("-- name: foo-bla()\nSELECT 1;\n" * 2, "sqlite3")
        pytest.fail("must reject homonymous queries")
    except SQLLoadException as e:
        assert "foo_bla" in str(e)
    # - is okay because mapped to _
    queries = aiosql.from_str("-- name: -dash()\nSELECT 1;\n", "sqlite3")
    assert "_dash" in queries.available_queries


def test_loading_query_signature_with_duplicate_parameter():
    sql_str = "-- name: get(foo)^\n" "select * from test where foo=:foo and foo=:foo"
    queries = aiosql.from_str(sql_str, "aiosqlite")
    assert queries.get.__signature__ == inspect.Signature(
        [
            inspect.Parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
            inspect.Parameter("foo", kind=inspect.Parameter.KEYWORD_ONLY),
        ]
    )


def test_adapters():
    try:
        aiosql.aiosql._make_driver_adapter("no-such-driver-adapter")
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "unregistered driver_adapter" in str(e)

    class PyFormatConnector:
        paramstyle = "pyformat"

    a = aiosql.aiosql._make_driver_adapter(PyFormatConnector)
    assert type(a) == aiosql.adapters.PyFormatAdapter

    class NamedConnector:
        paramstyle = "named"

    a = aiosql.aiosql._make_driver_adapter(NamedConnector)
    assert type(a) == aiosql.adapters.GenericAdapter

    class NoSuchConnector:
        paramstyle = "no-such-style"

    try:
        aiosql.aiosql._make_driver_adapter(NoSuchConnector)
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "Unexpected driver" in str(e)

    try:
        aiosql.aiosql._make_driver_adapter(True)  # type: ignore
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "Unexpected driver" in str(e)


def test_no_such_path():
    try:
        aiosql.from_path("/no/such/file", "sqlite3")
        pytest.fail("must raise an exception")  # pragma: no cover
    except SQLLoadException as e:
        assert "File does not exist" in str(e)


def test_file_loading(sql_file):
    db = aiosql.from_path(sql_file, "sqlite3")
    assert "get_user_blogs" in db.__dict__


def test_misc(sql_file):
    try:
        queries = aiosql.queries.Queries("sqlite3")
        queries._make_sync_fn(("hello", None, -1, "SELECT NULL;", None, None, None, None, None))
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "Unknown operation" in str(e)
    try:
        db = aiosql.from_str("-- name: a*b\nSELECT 'ab'\n", "sqlite3")
        pytest.fail("must raise en exception")  # pragma: no cover
    except Exception as e:
        assert "invalid query name and operation" in str(e)
    ql = aiosql.query_loader.QueryLoader(None, None)
    try:
        ql.load_query_data_from_dir_path(sql_file)
        pytest.fail("must raise en exception")  # pragma: no cover
    except ValueError as e:
        assert "must be a directory" in str(e)


def test_kwargs():
    # kwargs_only == True
    queries = aiosql.from_str(
        "-- name: plus_one(val)$\nSELECT 1 + :val;\n", "sqlite3", kwargs_only=True
    )
    import sqlite3

    conn = sqlite3.connect(":memory:")
    assert 42 == queries.plus_one(conn, val=41)
    try:
        queries.plus_one(conn, 2)
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "kwargs" in str(e)
    # kwargs_only == False
    queries = aiosql.from_str(
        "-- name: plus-two(val)$\nSELECT 2 + :val;\n", "sqlite3", kwargs_only=False
    )
    assert 42 == queries.plus_two(conn, val=40)
    try:
        queries.plus_two(conn, 2, val=41)
        pytest.fail("must raise an exception")  # pragma: no cover
    except ValueError as e:
        assert "mix" in str(e)

import sqlite3

PARAM_QUERIES = """
-- name: xlii()$
SELECT 42;

-- name: next(n)$
SELECT :n+1;

-- name: add(n, m)$
SELECT :n+:m;

-- name: sub(n, m)$
SELECT :n - :m;
"""

def run_param_queries(conn, kwargs_only: bool = True):
    q = aiosql.from_str(PARAM_QUERIES, "sqlite3", kwargs_only=kwargs_only)
    assert q.xlii(conn) == 42
    assert q.next(conn, n=41) == 42
    assert q.add(conn, n=19, m=23) == 42
    assert q.sub(conn, n=47, m=5) == 42
    # usage errors
    try:
        q.next(conn, 41)
        pytest.fail("must complain about positional parameter")
    except ValueError as e:
        assert "positional" in str(e)
    try:
        ft = q.sub(conn, 47, 5)
        if kwargs_only:
            pytest.fail("must complain about positional parameter")
        else:
            assert sys.version_info < (3, 14)
            assert ft == 42
    except sqlite3.ProgrammingError as e:  # scheduled deprecation
        assert sys.version_info >= (3, 14)
    except ValueError as e:
        assert "positional" in str(e)

def test_parameter_declarations():
    # ok
    conn = sqlite3.connect(":memory:")
    run_param_queries(conn, kwargs_only=True)
    run_param_queries(conn, kwargs_only=False)
    conn.close()
    # errors
    try:
        aiosql.from_str("-- name: foo()\nSELECT :N + 1;\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "undeclared" in str(e) and "N" in str(e)
    try:
        aiosql.from_str("-- name: foo(N, M)\nSELECT :N + 1;\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "unused" in str(e) and "M" in str(e)
    try:
        aiosql.from_str("-- name: foo(a)#\nCREATE TABLE :a();\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "script" in str(e)

def test_empty_query():
    try:
        aiosql.from_str("-- name: foo()\n--name: bla()\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty query" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- record_class: Foo\n--name: bla\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n \r\n\t  --name: bla()\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty query" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- just a comment\n--name: bla()\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- record_class: Foo\n-- just a comment\n--name: bla()\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- just a comment\n  ;  \n-- hop\n--name: bla()\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- just a comment\n;\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
    try:
        aiosql.from_str("-- name: foo()\n-- record_class: Foo\n-- just a comment\n;\n", "sqlite3")
        pytest.fail("must raise an exception")
    except SQLParseException as e:
        assert "empty sql" in str(e)
