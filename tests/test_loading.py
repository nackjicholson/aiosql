import inspect
from pathlib import Path
from unittest import mock

import aiosql
from aiosql.exceptions import SQLParseException
from aiosql.queries import Queries
from aiosql.query_loader import QueryLoader

import pytest


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


def test_no_such_path():
    try:
        aiosql.from_path("/no/such/file", "sqlite3")
        assert False, "must raise an exception"  # pragma: no cover
    except aiosql.exceptions.SQLLoadException as e:
        assert "File does not exist" in str(e)


def test_file_loading(sql_file):
    db = aiosql.from_path(sql_file, "sqlite3")
    assert "get_user_blogs" in db.__dict__


def test_misc(sql_file):
    try:
        aiosql.queries._make_sync_fn(("hello", None, -1, "SELECT NULL;", None, None))
        assert False, "must raise an exception"  # pragma: no cover
    except ValueError as e:
        assert "Unknown operation_type" in str(e)
    try:
        db = aiosql.from_str("-- name: a*b\nSELECT 'ab'\n", "sqlite3")
        assert False, "must raise en exception"  # pragma: no cover
    except Exception as e:
        assert "must convert to valid python variable" in str(e)
    ql = aiosql.query_loader.QueryLoader(None, None)
    try:
        ql.load_query_data_from_dir_path(sql_file)
        assert False, "must raise en exception"  # pragma: no cover
    except ValueError as e:
        assert "must be a directory" in str(e)
