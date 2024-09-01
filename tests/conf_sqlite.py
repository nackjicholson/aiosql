import pytest
import sqlite3
from pathlib import Path
from conf_schema import create_user_blogs, fill_user_blogs

def populate_sqlite3_db(db_path, queries):
    conn = sqlite3.connect(db_path)
    create_user_blogs(conn, queries)
    fill_user_blogs(conn, "sqlite")
    conn.close()
    # FIXME cleanup?!

@pytest.fixture
def sqlite3_db_path(tmpdir, queries):
    db_path = str(Path(tmpdir.strpath) / "blogdb.db")
    populate_sqlite3_db(db_path, queries)
    return db_path
