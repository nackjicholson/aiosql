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

    queries = aiosql.from_path(sql_dir, "sqlite3", queries_cls=TestQueries)
    assert isinstance(queries, TestQueries)


def test_frompath_queryloader_cls(sql_dir):
    mock_loader = mock.MagicMock(wraps=QueryLoader)

    aiosql.from_path(sql_dir, "sqlite3", loader_cls=mock_loader)

    assert mock_loader.called


def test_fromstr_queries_cls(sql):
    class TestQueries(Queries):
        pass

    queries = aiosql.from_str(sql, "sqlite3", queries_cls=TestQueries)
    assert isinstance(queries, TestQueries)


def test_fromstr_queryloader_cls(sql):
    mock_loader = mock.MagicMock(wraps=QueryLoader)

    aiosql.from_str(sql, "sqlite3", loader_cls=mock_loader)

    assert mock_loader.called


def test_trailing_space_on_lines_does_not_error():
    # There is whitespace in this string after the line ends
    sql_str = "-- name: trailing-space^    \n"
    sql_str += "select * from test;     \n"

    try:
        aiosql.from_str(sql_str, "sqlite3")
    except SQLParseException:
        pytest.fail("Raised SQLParseException due to trailing space in query.")
