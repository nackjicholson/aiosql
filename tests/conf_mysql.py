import pytest
import importlib
import utils as u
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

try:
    from pytest_mysql import factories

    @pytest.fixture
    def my_dsn(request):
        is_detached = request.config.getoption("mysql_detached")
        driver = request.config.getoption("mysql_driver")
        if is_detached:
            mp = request.getfixturevalue("mysql_noproc")
            # hmmm... pytest-mysql is a copy if the pg version so the
            # parameter is named "dbname" whereas mysql expects "database"
            dsn = {
                "password": request.config.getoption("mysql_passwd"),
                "database": request.config.getoption("mysql_dbname"),
            }
            # NOTE pip install mysql-connector-python
            if driver == "mysql.connector":
                dsn.update(auth_plugin="mysql_native_password")
        else:
            if not u.has_cmd("mysqld"):
                pytest.skip("test needs mysqld")
            mp = request.getfixturevalue("mysql_proc")
            assert mp.host == "localhost"
            # dsn = {"database": "test"}  # FIXME depends?
            dsn = {}
        # add common connection parameters
        dsn.update(user=mp.user, host=mp.host, port=mp.port)
        yield dsn

    @pytest.fixture
    def my_conn(request, my_dsn):
        driver = request.config.getoption("mysql_driver")
        db = importlib.import_module(driver)
        with db.connect(**my_dsn) as conn:
            yield conn

    @pytest.fixture
    def my_db(my_conn):

        # initial contents
        with my_conn.cursor() as cur:
            for ct in create_user_blogs("mysql"):
                cur.execute(ct)
            my_conn.commit()
            fill_user_blogs(cur, "mysql")
            my_conn.commit()

        yield my_conn

        # cleanup
        with my_conn.cursor() as cur:
            for dt in drop_user_blogs("mysql"):
                cur.execute(dt)
            my_conn.commit()

except ModuleNotFoundError:

    # provide empty fixtures to please pytest "parsing"

    @pytest.fixture
    def my_dsn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def my_conn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def my_db():
        raise Exception("undefined fixture")
