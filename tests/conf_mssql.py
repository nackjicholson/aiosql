import pytest
import importlib
import utils as u
import time
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

def ms_has_db(conn, database):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM sys.databases WHERE name = %s", (database,))
        return cursor.fetchone() in ({"cnt": 1}, (1,))

try:

    @pytest.fixture
    def ms_driver(request):
        """Return driver class."""
        driver = request.config.getoption("mssql_driver") or "pymssql"
        db = importlib.import_module(driver)
        return db

    @pytest.fixture
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
        }

    @pytest.fixture
    def ms_master(ms_dsn):
        """Return connection parameters suitable for "system admin" access."""
        dsn = dict(ms_dsn)
        dsn["database"] = "master"
        dsn["autocommit"] = True
        yield dsn

    @pytest.fixture
    def ms_conn(request, ms_dsn, ms_driver):
        """Return a simple connection using the expected driver."""
        driver, db = ms_driver.__name__, ms_driver
        tries = request.config.getoption("mssql_tries") or 3
        with u.db_connect(ms_driver, tries, **ms_dsn) as conn:
            yield conn

    @pytest.fixture
    def ms_db(ms_driver, ms_dsn, ms_master):
        """Build the test database and return a connection to that."""
        with ms_driver.connect(**ms_master) as conn:
            # initial contents if needed
            if not ms_has_db(conn, "pytest"):
                with conn.cursor() as cur:
                    cur.execute("CREATE DATABASE pytest")
                    cur.execute("USE pytest")
                    for ct in create_user_blogs("mssql"):
                        cur.execute(ct)
                    # conn.commit()
                    fill_user_blogs(cur, "mssql")
                    conn.commit()
            else:
                u.log.warning("skipping pytest schema creation")
        # connection to pytest possibly database created above
        with ms_driver.connect(**ms_dsn, autocommit=False) as conn:
            yield conn
        # cleanup:
        # with ms_driver.connect(**master, autocommit=True) as conn:
        #     with conn.cursor() as cur:
        #         u.log.warning("cleaning up pytest schema")
        #         cur.execute("DROP DATABASE pytest")

except ModuleNotFoundError:
    # provide empty fixtures to please pytest "parsing"

    @pytest.fixture
    def ms_driver():
        raise Exception("undefined fixture")

    @pytest.fixture
    def ms_dsn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def ms_master():
        raise Exception("undefined fixture")

    @pytest.fixture
    def ms_conn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def ms_db():
        raise Exception("undefined fixture")
