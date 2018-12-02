import asyncio
from pathlib import Path
from datetime import date

import aiosql
import asyncpg
import pytest


@pytest.fixture()
def queries():
    dir_path = Path(__file__).parent / "f1db/sql"
    return aiosql.from_path(dir_path, "asyncpg")


@pytest.mark.asyncio
async def test_record_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.get_drivers(conn)
    await conn.close()

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


@pytest.mark.asyncio
async def test_variable_replace_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    actual = await queries.get_drivers_born_after(conn, dob=date(1995, 1, 1))
    await conn.close()

    expected = [
        ("stroll", "STR", 18, date(1998, 10, 29)),
        ("leclerc", "LEC", 16, date(1997, 10, 16)),
        ("max_verstappen", "VER", 33, date(1997, 9, 30)),
        ("ocon", "OCO", 31, date(1996, 9, 17)),
        ("gasly", "GAS", 10, date(1996, 2, 7)),
        ("sirotkin", "SIR", 35, date(1995, 8, 27)),
    ]

    assert actual == expected


@pytest.mark.asyncio
async def test_create_returning_query(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        driverid = await queries.create_new_driver_pg(
            pool,
            driverref="vaughn",
            number=98,
            code="VAU",
            forename="William",
            surname="Vaughn",
            dob=date(1984, 6, 17),
            nationality="United States",
            url="https://gitlab.com/willvaughn",
        )

        async with pool.acquire() as conn:
            record = await conn.fetchrow(
                """\
                    select driverid,
                           code,
                           number
                      from drivers
                     where driverid = $1;""",
                driverid,
            )
            actual = tuple(record)

        expected = (21, "VAU", 98)

        assert actual == expected


@pytest.mark.asyncio
async def test_delete_query(pg_dsn, queries):
    conn = await asyncpg.connect(pg_dsn)
    # ocon lost his seat
    actual = await queries.delete_driver(conn, driverid=15)
    drivers = await queries.get_drivers(conn)
    await conn.close()

    assert actual is None
    assert len(drivers) == 19


@pytest.mark.asyncio
async def test_async_methods(pg_dsn, queries):
    async with asyncpg.create_pool(pg_dsn) as pool:
        spanish_drivers, french_drivers = await asyncio.gather(
            queries.get_drivers_by_nationality(pool, nationality="Spanish"),
            queries.get_drivers_by_nationality(pool, nationality="French"),
        )

    assert spanish_drivers == [
        (2, "alonso", 14, "ALO", "Fernando", "Alonso", date(1981, 7, 29), "Spanish"),
        (13, "sainz", 55, "SAI", "Carlos", "Sainz", date(1994, 9, 1), "Spanish"),
    ]
    assert french_drivers == [
        (5, "grosjean", 8, "GRO", "Romain", "Grosjean", date(1986, 4, 17), "French"),
        (15, "ocon", 31, "OCO", "Esteban", "Ocon", date(1996, 9, 17), "French"),
        (17, "gasly", 10, "GAS", "Pierre", "Gasly", date(1996, 2, 7), "French"),
    ]
