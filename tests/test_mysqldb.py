import datetime
import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import MySQLdb as db
except ModuleNotFoundError:
    pytest.skip("missing driver: MySQLdb (mysqlclient)", allow_module_level=True)

pytestmark = [
    pytest.mark.mysql,
    pytest.mark.skipif(not u.has_pkg("pytest_mysql"), reason="no pytest_mysql"),
]

@pytest.fixture(scope="module")
def driver():
    return "mysqldb"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest.fixture
def conn(my_db):
    return my_db

def test_my_dsn(my_dsn):
    assert "user" in my_dsn and "host" in my_dsn and "port" in my_dsn

def test_my_conn(conn):
    assert conn.__module__.startswith(db.__name__)
    t.run_something(conn)

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
    # FIXME
	# run_record_query as test_record_query,
	# run_parameterized_record_query as test_parameterized_record_query,
	run_parameterized_query as test_parameterized_query,
	run_record_class_query as test_record_class_query,
	run_select_cursor_context_manager as test_select_cursor_context_manager,
	run_select_one as test_select_one,
	# run_insert_returning as test_insert_returning,
	run_delete as test_delete,
	run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
	run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
    # FIXME kwargs -> args?
	# run_modulo as test_modulo,
)
