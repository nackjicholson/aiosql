import inspect
from pathlib import Path
from unittest import mock

import pytest
import aiosql

from aiosql.exceptions import SQLParseException
from aiosql.queries import Queries
from aiosql.query_loader import QueryLoader


@pytest.fixture
def sql_dir():
    return Path(__file__).parent / "blogdb/sql"


@pytest.fixture
def sql(sql_dir):
    with open(sql_dir / "blogs/blogs.sql") as f:
        return f.read()


def test_frompath_queries_cls(sql_dir):
    class TestQueries(Queries):
        pass

    queries = aiosql.from_path(sql_dir, "aiosqlite", queries_cls=TestQueries)
    assert isinstance(queries, TestQueries)


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
    except SQLParseException:
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
