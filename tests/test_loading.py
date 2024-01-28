import inspect
from pathlib import Path
from unittest import mock
import re

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

    queries = aiosql.from_path(sql_dir, "aiosqlite", queries_cls=TestQueries)
    assert isinstance(queries, TestQueries)

    assert repr(queries).startswith("Queries(")


def test_frompath_queryloader_cls(sql_dir):
    mock_loader = mock.MagicMock(wraps=QueryLoader)

    aiosql.from_path(sql_dir, "aiosqlite", loader_cls=mock_loader)

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
    sql_str = "-- name: trailing-space^    \n"
    sql_str += "select * from test;     \n"

    try:
        aiosql.from_str(sql_str, "aiosqlite")
    except SQLParseException:  # pragma: no cover
        pytest.fail("Raised SQLParseException due to trailing space in query.")


def test_non_ascii_char():
    # this triggers a warning, that we do not really check but for coverage
    q = aiosql.from_str("-- name: zéro\nSELECT 0;\n", "sqlite3")
    assert "zéro" in q._available_queries
    q = aiosql.from_str("-- name: éêèëÉÊÈË\nSELECT 'eeeeeeee!';\n", "sqlite3")
    assert "éêèëÉÊÈË" in q._available_queries
    q = aiosql.from_str("-- name: 안녕하세요\nSELECT 'hello!';\n", "sqlite3")
    assert "안녕하세요" in q._available_queries


def test_loading_query_signature():
    sql_str = "-- name: get^\n" "select * from test where foo=:foo and bar=:bar"
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
        queries = aiosql.from_str("-- name: 1st\nSELECT 1;\n", "sqlite3")
        assert False, "'1st' should be rejected"
    except SQLParseException as e:
        assert '"1st"' in str(e)
    try:
        queries = aiosql.from_str("-- name: one$garbage\nSELECT 1;\n", "sqlite3")
        assert False, "garbage should be rejected"
    except SQLParseException as e:
        assert 'garbage"' in str(e)
    # - is okay because mapped to _
    queries = aiosql.from_str("-- name: -dash\nSELECT 1;\n", "sqlite3")
    assert "_dash" in queries.available_queries


def test_loading_query_signature_with_duplicate_parameter():
    sql_str = "-- name: get^\n" "select * from test where foo=:foo and foo=:foo"
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
        assert False, "must raise an exception"  # pragma: no cover
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
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "Unexpected driver_adapter" in str(e)

    try:
        aiosql.aiosql._make_driver_adapter(True)  # type: ignore
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "Unexpected driver_adapter" in str(e)


def test_no_such_path():
    try:
        aiosql.from_path("/no/such/file", "sqlite3")
        assert False, "must raise an exception"  # pragma: no cover
    except SQLLoadException as e:
        assert "File does not exist" in str(e)


def test_file_loading(sql_file):
    db = aiosql.from_path(sql_file, "sqlite3")
    assert "get_user_blogs" in db.__dict__


def test_misc(sql_file):
    try:
        queries = aiosql.queries.Queries("sqlite3")
        queries._make_sync_fn(("hello", None, -1, "SELECT NULL;", None, None, None))
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "Unknown operation_type" in str(e)
    try:
        db = aiosql.from_str("-- name: a*b\nSELECT 'ab'\n", "sqlite3")
        assert False, "must raise en exception"  # pragma: no cover
    except Exception as e:
        assert "invalid query name and operation" in str(e)
    ql = aiosql.query_loader.QueryLoader(None, None)
    try:
        ql.load_query_data_from_dir_path(sql_file)
        assert False, "must raise en exception"  # pragma: no cover
    except ValueError as e:
        assert "must be a directory" in str(e)


def test_kwargs():
    # kwargs_only == True
    queries = aiosql.from_str("-- name: plus_one$\nSELECT 1 + :val;\n", "sqlite3", kwargs_only=True)
    import sqlite3

    conn = sqlite3.connect(":memory:")
    assert 42 == queries.plus_one(conn, val=41)
    try:
        queries.plus_one(conn, 2)
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "kwargs" in str(e)
    # kwargs_only == False
    queries = aiosql.from_str(
        "-- name: plus_two$\nSELECT 2 + :val;\n", "sqlite3", kwargs_only=False
    )
    assert 42 == queries.plus_two(conn, val=40)
    try:
        queries.plus_two(conn, 2, val=41)
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "mix" in str(e)
