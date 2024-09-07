import aiosql
import pytest
import run_tests as t
import sqlite3 as db
import utils

pytestmark = [
    pytest.mark.sqlite3
]

@pytest.fixture(scope="module")
def driver():
    return "sqlite3"

@pytest.fixture(scope="module")
def date():
    return t.todate

@pytest.fixture
def rconn(li_dbpath):
    conn = db.connect(li_dbpath)
    yield conn
    conn.close()

@pytest.fixture
def conn(li_db):
    return li_db

@pytest.fixture
def dconn(conn):
    conn.row_factory = utils.dict_factory
    return conn

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
	run_record_query as test_record_query,
	run_parameterized_query as test_parameterized_query,
	run_parameterized_record_query as test_parameterized_record_query,
	run_record_class_query as test_record_class_query,
	run_select_cursor_context_manager as test_select_cursor_context_manager,
	run_select_one as test_select_one,
	run_insert_returning as test_insert_returning,
	run_delete as test_delete,
	run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
	run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
	run_modulo as test_modulo,
)
