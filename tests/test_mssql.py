import datetime
import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import mssql_python as db  # Python MS SQL driver
except ModuleNotFoundError:
    pytest.skip("missing driver: mssql_python", allow_module_level=True)

pytestmark = [
    pytest.mark.mssql
]

connections: int = 0

@pytest.fixture(scope="module")
def driver():
    return "mssql-python"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest.fixture(scope="module")
def conn_str(ms_dsn):
    """Return connection string suitable for mssql-python driver."""
    return \
        f"Server={ms_dsn['server']},{ms_dsn['port']};" \
        f"Database={ms_dsn['database']};" \
        f"UID={ms_dsn['user']};" \
        f"PWD={ms_dsn['password']};" \
        r"Encrypt=yes;TrustServerCertificate=yes;"

@pytest.fixture
def conn(conn_str, ms_db):
    global connections
    conn_id = connections
    connections += 1
    u.log.debug(f"pytest connection [{conn_id}]")
    with db.connect(conn_str, autocommit=False) as conn:
        yield conn
    u.log.debug(f"pytest deconnection [{conn_id}]")

@pytest.fixture
def dconn(conn):
    yield conn

@pytest.fixture(scope="module")
def master_conn(conn_str, ms_dsn):
    # mssql seems to need autocommit for DDL
    master_conn_str = conn_str.replace(f"Database={ms_dsn['database']};", "Database=master;")
    global connections
    conn_id = connections
    connections += 1
    u.log.debug(f"master connection [{conn_id}]")
    with db.connect(master_conn_str, autocommit=True) as conn:
        yield conn
    u.log.debug(f"master deconnection [{connections}]")

# NOTE master_conn needed so that "pytest" database exists
def test_sanity_conn_str(conn_str, ms_db):
    global connections
    conn_id = connections
    connections += 1
    u.log.debug(f"pytest connection [{conn_id}]")
    with db.connect(conn_str) as conn:
        t.run_sanity(conn)
    u.log.debug(f"pytest deconnection [{conn_id}]")

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
