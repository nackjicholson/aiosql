import pytest
import importlib
import utils as u
import time
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

try:
    from pytest_mysql import factories

    @pytest.fixture
    def my_dsn(request):
        """Return connection parameters suitable to target driver."""
        is_detached = request.config.getoption("mysql_detached")
        driver = request.config.getoption("mysql_driver")
        database = request.config.getoption("mysql_dbname") or "test"
        if is_detached:
            mp = request.getfixturevalue("mysql_noproc")
            dsn = {
                "password": request.config.getoption("mysql_passwd"),
            }
        else:
            if not u.has_cmd("mysqld"):
                pytest.skip("test needs mysqld")
            mp = request.getfixturevalue("mysql_proc")
            # u.log.debug(f"mp: {mp}")
            # this fixture creates the database as a side effect
            conn = request.getfixturevalue("mysql")
            # u.log.debug(f"conn: {conn}")
            assert mp.running()
            assert mp.host == "localhost"
            # dsn = {"database": "test"} # if driver == "mysql.connector" else {}
            # NOTE mysql complains about host even if a unix socket is used:-/
            dsn = {"unix_socket": mp.unixsocket}
        # add common connection parameters… although host may be unused
        dsn.update(user=mp.user, host=mp.host, port=mp.port, database=database)
        # FIXME passwd?
        # NOTE pip install mysql-connector-python
        # TODO check for mysql.connector version ?
        if driver == "mysql.connector":
            dsn.update(auth_plugin="mysql_native_password")
        u.log.debug(f"my_dsn for {driver}: {dsn}")
        yield dsn

    @pytest.fixture
    def my_driver(request):
        driver = request.config.getoption("mysql_driver")
        db = importlib.import_module(driver)
        return db

    @pytest.fixture
    def my_conn(request, my_dsn, my_driver):
        """Return a connection using the expected driver."""
        tries = request.config.getoption("mysql_tries")
        fails = 0
        while tries > 0:
            tries -= 1
            try:
                with my_driver.connect(**my_dsn) as conn:
                    tries = 0
                    yield conn
            except Exception as e:
                fails += 1
                u.log.warning(f"{driver} connection failed ({fails}): {e}")
                time.sleep(1.0)

    @pytest.fixture
    def my_db(my_conn, queries):
        """Build the test database."""
        create_user_blogs(my_conn, queries)
        fill_user_blogs(my_conn, queries)
        yield my_conn
        drop_user_blogs(my_conn, queries)

except ModuleNotFoundError:
    # provide empty fixtures to please pytest "parsing"

    @pytest.fixture
    def my_dsn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def my_driver():
        raise Exception("undefined fixture")

    @pytest.fixture
    def my_conn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def my_db():
        raise Exception("undefined fixture")
