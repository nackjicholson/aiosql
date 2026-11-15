import pytest
import importlib
import utils as u
import time
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

# NOTE pymssql and mssql-python both support the pyformat syntax
def ms_has_db(conn, database):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM sys.databases WHERE name = %(database)s", {"database": database})
        return cursor.fetchone() in ({"cnt": 1}, (1,))

@pytest.fixture(scope="module")
def ms_dsn(request):
    """Return connection parameters suitable to pymssql driver."""
    yield {
        # see conftest.py for list of options
        "server": request.config.getoption("mssql_server") or '.',
        "port": request.config.getoption("mssql_port") or 1433,
        "user": request.config.getoption("mssql_user") or "sa",
        "password": request.config.getoption("mssql_password"),
        "database": request.config.getoption("mssql_database") or "pytest",
        "as_dict": True,
        "autocommit": False,
    }

@pytest.fixture(scope="module")
def ms_db(master_conn, queries):
    """Build the test database and return an admin connection to that."""
    need_db = not ms_has_db(master_conn, "pytest")
    # initial contents if needed
    if need_db:
        with master_conn.cursor() as cur:
            cur.execute("CREATE DATABASE pytest")
            cur.execute("USE pytest")
            create_user_blogs(master_conn, queries)
            fill_user_blogs(master_conn, queries)
    else:
        u.log.warning("skipping pytest database and schema creation")
    yield master_conn
    # cleanup (some issues with mssql-python because database is still in use)
    if need_db:  # also do the cleanup
        try:
            with master_conn.cursor() as cur:
                drop_user_blogs(master_conn, queries)
                cur.execute("USE master")
                cur.execute("DROP DATABASE pytest")
        except Exception as e:
            u.log.warning(f"cannot DROP DATABASE pytest: {e}")
            # raise?
