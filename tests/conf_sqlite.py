import pytest
import sqlite3
from pathlib import Path
from conf_schema import create_user_blogs, fill_user_blogs


def populate_sqlite3_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("\n".join(create_user_blogs("sqlite")))
    fill_user_blogs(cur, "sqlite")
    conn.commit()
    conn.close()


@pytest.fixture
def sqlite3_db_path(tmpdir):
    db_path = str(Path(tmpdir.strpath) / "blogdb.db")
    populate_sqlite3_db(db_path)
    return db_path
