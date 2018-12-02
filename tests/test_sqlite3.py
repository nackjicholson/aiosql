from pathlib import Path

import aiosql
import pytest


@pytest.fixture()
def queries():
    p = Path(__file__).parent / "f1db/sql/drivers.sql"
    with p.open() as fp:
        sql = fp.read()
        return aiosql.from_str(sql, "sqlite3")


def test_record_query(sqlite3_conn, queries):
    actual = queries.get_drivers(sqlite3_conn)

    assert len(actual) == 20
    assert actual[0] == {
        "driverid": 1,
        "driverref": "hamilton",
        "number": 44,
        "code": "HAM",
        "forename": "Lewis",
        "surname": "Hamilton",
        "dob": "1985-01-07",
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
        "dob": "1995-08-27",
        "nationality": "Russian",
        "url": "http://en.wikipedia.org/wiki/Sergey_Sirotkin_(racing_driver)",
    }


def test_variable_replace_query(sqlite3_conn, queries):
    actual = queries.get_drivers_born_after(sqlite3_conn, dob="1995-01-01")

    expected = [
        ("stroll", "STR", 18, "1998-10-29"),
        ("leclerc", "LEC", 16, "1997-10-16"),
        ("max_verstappen", "VER", 33, "1997-09-30"),
        ("ocon", "OCO", 31, "1996-09-17"),
        ("gasly", "GAS", 10, "1996-02-07"),
        ("sirotkin", "SIR", 35, "1995-08-27"),
    ]

    assert actual == expected


def test_create_returning_query(sqlite3_conn, queries):
    driverid = queries.create_new_driver(
        sqlite3_conn,
        driverref="vaughn",
        number=98,
        code="VAU",
        forename="William",
        surname="Vaughn",
        dob="1984-06-17",
        nationality="United States",
        url="https://gitlab.com/willvaughn",
    )

    cur = sqlite3_conn.cursor()
    cur.execute(
        """\
        select driverid,
               code,
               number
          from drivers
         where driverid = ?;
    """,
        (driverid,),
    )
    actual = cur.fetchall()
    cur.close()
    expected = [(21, "VAU", 98)]

    assert actual == expected


def test_delete_query(sqlite3_conn, queries):
    # ocon lost his seat
    actual = queries.delete_driver(sqlite3_conn, driverid=15)
    assert actual is None

    drivers = queries.get_drivers(sqlite3_conn)
    assert len(drivers) == 19
