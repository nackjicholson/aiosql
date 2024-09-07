import datetime
import aiosql
import pytest
import run_tests as t
import utils as u

try:
    import pg8000 as db
except ModuleNotFoundError:
    pytest.skip("missing driver: pg8000", allow_module_level=True)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(not u.has_pkg("pytest_postgresql"), reason="no pytest_postgresql"),
]

@pytest.fixture(scope="module")
def driver():
    return "pg8000"

@pytest.fixture(scope="module")
def date():
    return datetime.date

@pytest.fixture
def rconn(pg_params, pg_conn):
    params = dict(pg_params)
    params["database"] = params["dbname"]
    del params["dbname"]
    # cleanup unsupported keyword arguments
    for kw in ("sslcertmode", "connect_timeout", "hostaddr"):
        if kw in params:
            del params[kw]
    u.log.debug(f"params: {params}")
    with db.connect(**params) as conn:
        yield conn

@pytest.fixture
def conn(pg_db):
    yield pg_db

# TODO dconn: dict result is not supported

from run_tests import (
    run_sanity as test_sanity,
	run_something as test_something,
	run_cursor as test_cursor,
	# run_record_query as test_record_query,
	# run_parameterized_record_query as test_parameterized_record_query,
	run_parameterized_query as test_parameterized_query,
	run_record_class_query as test_record_class_query,
	run_select_cursor_context_manager as test_select_cursor_context_manager,
	run_select_one as test_select_one,
	run_insert_returning as test_insert_returning,
	run_delete as test_delete,
	run_insert_many as test_insert_many,
	run_select_value as test_select_value,
	run_date_time as test_date_time,
    # FIXME not supported?
	# run_object_attributes as test_object_attributes,
	run_execute_script as test_execute_script,
	run_modulo as test_modulo,
)
