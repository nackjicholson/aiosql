import datetime
import aiosql
import pytest
import run_tests as t
import utils as u

DB = "mssql"
DRIVER = "pymssql"

try:
    import pymssql as db  # Python MS SQL driver
except ModuleNotFoundError:
    pytest.skip(f"missing driver: {DRIVER}", allow_module_level=True)

pytestmark = [
    pytest.mark.mssql,
    pytest.mark.skipif(not u.has_pkg(DRIVER), reason=f"no {DRIVER}"),
]

@pytest.fixture
def queries():
    return t.queries(DRIVER)

@pytest.fixture
def conn(ms_db):
    yield ms_db

@pytest.fixture
def date():
    return datetime.date

def test_sanity_master(ms_master):
    with db.connect(**ms_master) as conn:
        t.run_sanity(conn)

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
	run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
	run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
	run_modulo as test_modulo,
)
