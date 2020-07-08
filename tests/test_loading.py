from pathlib import Path
from unittest import mock

import pytest
import aiosql

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
