import pytest
import re

from pathlib import Path
from aiosql import DB

SQL = Path(__file__).parent / "test_db.sql"


def run_42(db: DB):
    assert db is not None
    cur = db.cursor()
    cur.execute("SELECT 42 AS fourtytwo")
    assert cur.description[0][0] == "fourtytwo"
    assert cur.fetchone()[0] == 42
    db.close()
    db.connect()


def run_stuff(db: DB):
    assert db is not None
    db.create_foo()
    assert db.count_foo()[0][0] == 0
    db.insert_foo(pk=1, val="one")
    assert db.count_foo()[0][0] == 1
    db.insert_foo(pk=2, val="two")
    db.commit()
    assert db.count_foo()[0][0] == 2
    assert re.search(r"two", db.select_foo_pk(pk=2)[0][0])
    db.update_foo_pk(pk=2, val="deux")
    db.delete_foo_pk(pk=1)
    db.commit()
    assert db.count_foo()[0][0] == 1
    assert re.search(r"deux", db.select_foo_pk(pk=2)[0][0])
    db.delete_foo_all()
    db.commit()
    assert db.count_foo()[0][0] == 0
    db.insert_foo(pk=3, val="three")
    db.insert_foo(pk=4, val="four")
    db.insert_foo(pk=5, val="five")
    assert db.count_foo()[0][0] == 3
    db.rollback()
    assert db.count_foo()[0][0] == 0
    db.drop_foo()
    db.commit()
    db.close()
    db.connect()
    run_42(db)


def test_sqlite():
    db = DB("sqlite", ":memory:", SQL, '{"check_same_thread":False}')
    run_stuff(db)
    db.close()


def test_options():
    db = DB("sqlite", ":memory:", SQL, timeout=10, check_same_thread=False, isolation_level=None)
    run_42(db)
    db.close()
    db = DB(
        "sqlite",
        ":memory:",
        SQL,
        {"timeout": 10, "check_same_thread": False, "isolation_level": None},
    )
    run_42(db)
    db.close()
    db = DB(
        "sqlite",
        ":memory:",
        SQL,
        '{"timeout":10, "check_same_thread":False, "isolation_level":None}',
    )
    run_42(db)
    db.close()


@pytest.fixture
def pg_conn(postgresql):
    with postgresql as pg:
        p = pg.get_dsn_parameters()
        return "postgres://{user}@{host}:{port}/{dbname}".format(**p)


def test_postgres(pg_conn):
    assert re.match("postgres://", pg_conn)
    db = DB("postgres", pg_conn, SQL)
    run_stuff(db)
    db.close()


def test_from_str():
    db = DB("sqlite", ":memory:")
    db.add_queries_from_str("-- name: next\nSELECT :arg + 1 AS next;\n")
    assert db.next(arg=1)[0][0] == 2
    db.add_queries_from_str("-- name: prev\nSELECT :arg - 1 AS prev;\n")
    assert db.next(arg=41)[0][0] == 42
    assert db.prev(arg=42)[0][0] == 41
    # override previous definition
    db.add_queries_from_str("-- name: foo\nSELECT :arg + 42 AS foo;\n")
    assert db.foo(0)[0][0] == 42
    db.add_queries_from_str("-- name: foo\nSELECT :arg - 42 AS foo;\n")
    assert db.foo(42)[0][0] == 0
    assert db.next(arg=42)[0][0] == 43
    assert db.prev(arg=43)[0][0] == 42
    assert sorted(db._available_queries) == [
        "foo",
        "foo_cursor",
        "next",
        "next_cursor",
        "prev",
        "prev_cursor",
    ]
    db.close()


def test_misc():
    try:
        db = DB("foodb", "aiodb", SQL)
        assert False, "there is no foodb"
    except Exception as err:
        assert True, "foodb is not supported"
