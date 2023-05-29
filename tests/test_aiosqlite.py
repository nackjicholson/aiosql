import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import aiosqlite
except ModuleNotFoundError:
    pytest.skip("missing driver: aiosqlite", allow_module_level=True)

pytestmark = [
    pytest.mark.sqlite3,
    # pytest.mark.asyncio,
    pytest.mark.skipif(not u.has_pkg("pytest_asyncio"), reason="no pytest_asyncio"),
]

DRIVER = "aiosqlite"


@pytest.fixture
def queries():
    return t.queries("aiosqlite")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# NOTE no cursor on aiosqlite driver adapter
# def test_cursor(conn, queries):
#    t.run_cursor(conn, queries)


@pytest.mark.asyncio
async def test_record_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        await t.run_async_record_query(conn, queries)


@pytest.mark.asyncio
async def test_parameterized_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_parameterized_query(conn, queries, t.todate)


@pytest.mark.asyncio
async def test_parameterized_record_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        await t.run_async_parameterized_record_query(conn, queries, DRIVER, t.todate)


@pytest.mark.asyncio
async def test_record_class_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_record_class_query(conn, queries, t.todate)


@pytest.mark.asyncio
async def test_select_cursor_context_manager(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_select_cursor_context_manager(conn, queries, t.todate)


@pytest.mark.asyncio
async def test_select_one(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_select_one(conn, queries)


@pytest.mark.asyncio
async def test_select_value(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_select_value(conn, queries)


@pytest.mark.asyncio
async def test_insert_returning(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_insert_returning(conn, queries, DRIVER, t.todate)


@pytest.mark.asyncio
async def test_delete(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_delete(conn, queries)


@pytest.mark.asyncio
async def test_insert_many(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        await t.run_async_insert_many(conn, queries, t.todate)


@pytest.mark.asyncio
async def test_async_methods(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        conn.row_factory = dict_factory
        await t.run_async_methods(conn, queries)


@pytest.mark.asyncio
async def test_execute_script(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.comments.sqlite_create_comments_table(conn)
        assert actual == "DONE"
