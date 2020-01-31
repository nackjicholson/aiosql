import pytest

from tests.conftest import BLOGDB_PATH
from tests.test_aiosqlite import aiosqlite_queries
from tests.test_asyncpg import asyncpg_queries
from tests.test_psycopg2 import psycopg2_queries
from tests.test_sqlite3 import sqlite3_queries

blogs_files_fn = [
    ("blogs", "blogs.sql", ["publish_blog", "remove_blog", "get_user_blogs"]),
    (
        "blogs",
        "blogs_pg.sql",
        ["pg_get_blogs_published_after", "pg_publish_blog", "pg_bulk_publish"],
    ),
    ("blogs", "blogs_sqlite.sql", ["sqlite_get_blogs_published_after", "sqlite_bulk_publish"]),
    ("users", "users.sql", ["get_all", "get_by_username", "get_by_lastname", "get_all_sorted"]),
]

drivers = [
(aiosqlite_queries()), (asyncpg_queries()), (psycopg2_queries()),(sqlite3_queries())
]


@pytest.mark.parametrize("queries", drivers)
@pytest.mark.parametrize("dir, file, functions", blogs_files_fn)
def test_introspected_queries_path(queries, dir, file, functions):

    for fn in functions:
        assert (
            queries.__getattribute__(dir).__getattribute__(fn).file_path
            == BLOGDB_PATH / "sql" / dir / file
        )
