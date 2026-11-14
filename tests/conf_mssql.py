import pytest
import importlib
import utils as u
import time
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

# NOTE pymssql and mssql-python support the pyformat syntax
def ms_has_db(conn, database):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM sys.databases WHERE name = %(database)s", {"database": database})
        return cursor.fetchone() in ({"cnt": 1}, (1,))

try:
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
        """Build the test database and return a connection to that."""
        # initial contents if needed
        if not ms_has_db(master_conn, "pytest"):
            with master_conn.cursor() as cur:
                cur.execute("CREATE DATABASE pytest")
                cur.execute("USE pytest")
            create_user_blogs(master_conn, queries)
            fill_user_blogs(master_conn, queries)
        else:
            u.log.warning("skipping pytest schema creation")
        # connection to pytest possibly database created above
        yield master_conn
        # cleanup
        with master_conn.cursor() as cur:
            # u.log.warning("cleaning up pytest schema")
            cur.execute("USE master")
            cur.execute("DROP DATABASE pytest")

except ModuleNotFoundError:
    # provide empty fixtures to please pytest "parsing"

    @pytest.fixture
    def ms_driver():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def ms_dsn():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def ms_master():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def ms_conn():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def ms_db():
        raise Exception("unimplemented fixture")
