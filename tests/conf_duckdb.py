import pytest
from pathlib import Path
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs

try:
    import duckdb

    @pytest.fixture
    def duckdb_conn(queries):
        # db_path = str(Path(tmpdir.strpath) / "blogdb.duck.db")
        conn = duckdb.connect(":memory:")
        create_user_blogs(conn, queries)
        fill_user_blogs(conn, queries)
        yield conn
        drop_user_blogs(conn, queries)

except ModuleNotFoundError:

    @pytest.fixture
    def duckdb_conn():
        raise Exception("unimplemented fixture")
