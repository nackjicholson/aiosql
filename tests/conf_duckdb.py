import pytest
from pathlib import Path
from conf_schema import USERS_DATA_PATH, BLOGS_DATA_PATH, create_user_blogs, drop_user_blogs

try:
    import duckdb

    @pytest.fixture
    def duckdb_conn(queries):
        # db_path = str(Path(tmpdir.strpath) / "blogdb.duck.db")
        conn = duckdb.connect(":memory:")
        create_user_blogs(conn, queries)
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
        conn.commit()
        yield conn
        drop_user_blogs(conn, queries)
        conn.close()

except ModuleNotFoundError:

    @pytest.fixture
    def duckdb_conn():
        raise Exception("undefined fixture")
