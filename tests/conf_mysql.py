import pytest
from pytest_mysql import factories as my_factories
from conf_schema import create_user_blogs, fill_user_blogs


@pytest.fixture
def my_dsn(mysql_proc):
    mp = mysql_proc
    assert mp.host == "localhost"
    yield {
        "user": mp.user,
        # "password": mp.password,
        "host": mp.host,
        "port": mp.port,
        # "database": mp.dbname,
    }


@pytest.fixture
def my_db(mysql):
    with mysql.cursor() as cur:
        for tc in create_user_blogs("mysql"):
            cur.execute(tc)
        mysql.commit()
        fill_user_blogs(cur, "mysql")
        mysql.commit()
    yield mysql
    # FIXME mysql.commit()
