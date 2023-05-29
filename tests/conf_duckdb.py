import pytest
from pathlib import Path
from conf_schema import create_user_blogs, USERS_DATA_PATH, BLOGS_DATA_PATH

try:
    import duckdb

    @pytest.fixture
    def duckdb_db_path(tmpdir):
        db_path = str(Path(tmpdir.strpath) / "blogdb.duck.db")
        return db_path

    @pytest.fixture
    def duckdb_conn(duckdb_db_path):
        conn = duckdb.connect(":memory:")
        populate_duckdb_db(conn)
        yield conn
        conn.close()

    def populate_duckdb_db(conn):
        conn.execute("\n".join(create_user_blogs("duckdb")))
        conn.execute(
            "insert into users(userid, username, firstname, lastname)\n"
            "select nextval('users_seq') as userid, column0 as username,\n"
            "       column1 as firstname, column2 as lastname\n"
            f"from read_csv_auto('{str(USERS_DATA_PATH)}', header=False)"
        )
        conn.execute(
            "insert into blogs(blogid, userid, title, content, published)\n"
            "select nextval('blogs_seq') as blogid, column0 as userid, column1 as title,\n"
            "       column2 as content, column3 as published\n"
            f"from read_csv_auto('{str(BLOGS_DATA_PATH)}', header=False)"
        )

except ModuleNotFoundError:

    @pytest.fixture
    def duckdb_db_path(tmpdir):
        raise Exception("undefined fixture")

    @pytest.fixture
    def duckdb_conn(duckdb_db_path):
        raise Exception("undefined fixture")
