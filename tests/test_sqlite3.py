import aiosql
import pytest
import run_tests as t
import sqlite3 as db

pytestmark = [pytest.mark.sqlite3]

DRIVER = "sqlite3"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@pytest.fixture
def queries():
    return t.queries(DRIVER)

@pytest.fixture
def conn(sqlite3_db_path):
    conn = db.connect(sqlite3_db_path)
    yield conn
    conn.close()

@pytest.fixture
def dconn(conn):
    conn.row_factory = dict_factory
    return conn

@pytest.fixture
def date():
    return t.todate

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
