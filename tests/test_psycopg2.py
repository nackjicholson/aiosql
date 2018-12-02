from datetime import date
from pathlib import Path

import aiosql
import pytest


@pytest.fixture()
def queries():
    dir_path = Path(__file__).parent / "f1db/sql"
    return aiosql.from_path(dir_path, "psycopg2")


def test_record_query(pg_conn, queries):
    actual = queries.get_drivers(pg_conn)

    assert len(actual) == 20
    assert actual[0] == {
        "driverid": 1,
        "driverref": "hamilton",
        "number": 44,
        "code": "HAM",
        "forename": "Lewis",
        "surname": "Hamilton",
        "dob": date(1985, 1, 7),
        "nationality": "British",
        "url": "http://en.wikipedia.org/wiki/Lewis_Hamilton",
    }
    assert actual[19] == {
        "driverid": 20,
        "driverref": "sirotkin",
        "number": 35,
        "code": "SIR",
        "forename": "Sergey",
        "surname": "Sirotkin",
        "dob": date(1995, 8, 27),
        "nationality": "Russian",
        "url": "http://en.wikipedia.org/wiki/Sergey_Sirotkin_(racing_driver)",
    }


def test_variable_replace_query(pg_conn, queries):
    actual = queries.get_drivers_born_after(pg_conn, dob="1995-01-01")

    expected = [
        ("stroll", "STR", 18, date(1998, 10, 29)),
        ("leclerc", "LEC", 16, date(1997, 10, 16)),
        ("max_verstappen", "VER", 33, date(1997, 9, 30)),
        ("ocon", "OCO", 31, date(1996, 9, 17)),
        ("gasly", "GAS", 10, date(1996, 2, 7)),
        ("sirotkin", "SIR", 35, date(1995, 8, 27)),
    ]

    assert actual == expected


def test_create_returning_query(pg_conn, queries):
    driverid = queries.create_new_driver_pg(
        pg_conn,
        driverref="vaughn",
        number=98,
        code="VAU",
        forename="William",
        surname="Vaughn",
        dob="1984-06-17",
        nationality="United States",
        url="https://gitlab.com/willvaughn",
    )

    with pg_conn.cursor() as cur:
        cur.execute(
            """\
            select driverid,
                   code,
                   number
              from drivers
             where driverid = %s;
        """,
            (driverid,),
        )
        actual = cur.fetchall()
    expected = [(21, "VAU", 98)]

    assert actual == expected


def test_delete_query(pg_conn, queries):
    # ocon lost his seat
    actual = queries.delete_driver(pg_conn, driverid=15)
    assert actual is None

    drivers = queries.get_drivers(pg_conn)
    assert len(drivers) == 19
