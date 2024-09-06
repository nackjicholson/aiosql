import pytest
from pathlib import Path
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs
import utils

@pytest.fixture
def li_dbpath(tmpdir):
    db_path = str(Path(tmpdir.strpath) / "blogdb.db")
    utils.log.warning(f"path = {db_path}")
    yield db_path

@pytest.fixture
def li_db(rconn, queries):
    utils.log.warning("sqlite creating blogdb…")
    create_user_blogs(rconn, queries)
    fill_user_blogs(rconn, queries)
    yield rconn
    drop_user_blogs(rconn, queries)
