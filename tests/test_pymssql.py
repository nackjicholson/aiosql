import datetime
import aiosql
import pytest
import run_tests as t

try:
    import pymssql as db  # Python MS SQL driver
except ModuleNotFoundError:
    pytest.skip("missing driver: pymssql", allow_module_level=True)

pytestmark = [
    pytest.mark.mssql
]

@pytest.fixture(scope="module")
def driver():
    return "pymssql"

@pytest.fixture(scope="module")
def date():
    return datetime.date

# user connections
@pytest.fixture
def conn(ms_dsn, ms_db):
    with db.connect(**ms_dsn) as conn:
        yield conn

@pytest.fixture
def dconn(conn, ms_db):
    yield conn

# global admin connection
@pytest.fixture(scope="module")
def master_conn(ms_dsn):
    ms_dsn_master = dict(ms_dsn)
    ms_dsn_master["database"] = "master"
    ms_dsn_master["autocommit"] = True
    with db.connect(**ms_dsn_master) as conn:
        yield conn

def test_sanity_master(master_conn):
    t.run_sanity(master_conn)

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
	run_record_query as test_record_query,
	run_parameterized_query as test_parameterized_query,
	run_parameterized_record_query as test_parameterized_record_query,
    # FIXME broken with is_dict
	# run_record_class_query as test_record_class_query,
	run_select_cursor_context_manager as test_select_cursor_context_manager,
	run_select_one as test_select_one,
	run_insert_returning as test_insert_returning,
	run_delete as test_delete,
    # FIXME broken?
	# run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
	run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
	run_modulo as test_modulo,
)
