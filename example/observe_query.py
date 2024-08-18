import time
import logging
import contextlib
import pg_execute_values as pev

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("metrics")

def report_metrics(op, sql, op_time):
    log.info(f"Operation: {op.name!r}\nSQL: {sql!r} \nTime (ms): {op_time}")

@contextlib.contextmanager
def observe_query(func):
    op = func.operation
    sql = func.sql
    start = time.time()
    yield
    end = time.time()
    op_time = end - start
    report_metrics(op, sql, op_time)

with observe_query(pev.queries.getem):
    pev.queries.getem(pev.conn)

# INFO:metrics:Operation: 'SELECT'
# SQL: 'select * from test order by id;' 
# Time (ms): 2.6226043701171875e-06
