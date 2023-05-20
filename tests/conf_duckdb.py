import pytest
import duckdb
from pathlib import Path
from conf_schema import create_user_blogs, USERS_DATA_PATH, BLOGS_DATA_PATH


@pytest.fixture()
def duckdb_db_path(tmpdir):
    db_path = str(Path(tmpdir.strpath) / "blogdb.duck.db")
    return db_path


@pytest.fixture(name="conn")
def duckdb_conn(duckdb_db_path):
    conn = duckdb.connect(":memory:")
    populate_duckdb_db(conn)
    yield conn
    conn.close()


def populate_duckdb_db(conn):
    conn.execute("\n".join(create_user_blogs("duckdb")))
    conn.execute(
        f"insert into users(userid, username, firstname, lastname) select nextval('users_seq') userid, column0 as username, column1 as firstname, column2 as lastname from read_csv_auto('{str(USERS_DATA_PATH)}', header=False)"
    )
    conn.execute(
        f"insert into blogs(blogid, userid, title, content, published) select nextval('blogs_seq') blogid, column0 as userid, column1 as title, column2 as content, column3 as published from read_csv_auto('{str(BLOGS_DATA_PATH)}', header=False)"
    )
