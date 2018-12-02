import asyncio
from pathlib import Path

import aiosql
import aiosqlite
import pytest


@pytest.fixture()
def queries():
    dir_path = Path(__file__).parent / "f1db/sql"
    return aiosql.from_path(dir_path, "aiosqlite")


@pytest.mark.asyncio
async def test_record_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.get_drivers(conn)

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


@pytest.mark.asyncio
async def test_variable_replace_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        actual = await queries.get_drivers_born_after(conn, dob="1995-01-01")

        expected = [
            ("stroll", "STR", 18, "1998-10-29"),
            ("leclerc", "LEC", 16, "1997-10-16"),
            ("max_verstappen", "VER", 33, "1997-09-30"),
            ("ocon", "OCO", 31, "1996-09-17"),
            ("gasly", "GAS", 10, "1996-02-07"),
            ("sirotkin", "SIR", 35, "1995-08-27"),
        ]

        assert actual == expected


@pytest.mark.asyncio
async def test_create_returning_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        driverid = await queries.create_new_driver(
            conn,
            driverref="vaughn",
            number=98,
            code="VAU",
            forename="William",
            surname="Vaughn",
            dob="1984-06-17",
            nationality="United States",
            url="https://gitlab.com/willvaughn",
        )

        cur = await conn.execute(
            """\
            select driverid,
                   code,
                   number
              from drivers
             where driverid = ?;
        """,
            (driverid,),
        )
        actual = await cur.fetchall()
        expected = [(21, "VAU", 98)]

        assert actual == expected


@pytest.mark.asyncio
async def test_delete_query(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        # ocon lost his seat
        actual = await queries.delete_driver(conn, driverid=15)
        assert actual is None

        drivers = await queries.get_drivers(conn)
        assert len(drivers) == 19


@pytest.mark.asyncio
async def test_async_methods(sqlite3_db_path, queries):
    async with aiosqlite.connect(sqlite3_db_path) as conn:
        spanish_drivers, french_drivers = await asyncio.gather(
            queries.get_drivers_by_nationality(conn, nationality="Spanish"),
            queries.get_drivers_by_nationality(conn, nationality="French"),
        )

        assert spanish_drivers == [
            (2, "alonso", 14, "ALO", "Fernando", "Alonso", "1981-07-29", "Spanish"),
            (13, "sainz", 55, "SAI", "Carlos", "Sainz", "1994-09-01", "Spanish"),
        ]
        assert french_drivers == [
            (5, "grosjean", 8, "GRO", "Romain", "Grosjean", "1986-04-17", "French"),
            (15, "ocon", 31, "OCO", "Esteban", "Ocon", "1996-09-17", "French"),
            (17, "gasly", 10, "GAS", "Pierre", "Gasly", "1996-02-07", "French"),
        ]
