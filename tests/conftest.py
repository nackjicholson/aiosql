import csv
import sqlite3
from pathlib import Path

import pytest

F1DB_PATH = Path(__file__).parent / "f1db"
DRIVERS_DATA_PATH = F1DB_PATH / "data/drivers_data.csv"


def populate_sqlite3_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """\
            create table drivers (
                driverid integer not null primary key,
                driverref text not null,
                number integer not null,
                code text not null,
                forename text not null,
                surname text not null,
                dob date not null,
                nationality text not null,
                url text unique
            );"""
    )

    with DRIVERS_DATA_PATH.open() as fp:
        reader = csv.reader(fp)
        rows = list(reader)

    cur.executemany(
        """\
            insert into drivers (
                driverref,
                number,
                code,
                forename,
                surname,
                dob,
                nationality,
                url
            ) values (?, ?, ?, ?, ?, ?, ?, ?);""",
        rows,
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def sqlite3_db_path(tmpdir):
    db_path = str(Path(tmpdir.strpath) / "f1db.db")
    populate_sqlite3_db(db_path)
    return db_path


@pytest.fixture()
def sqlite3_conn(sqlite3_db_path):
    conn = sqlite3.connect(sqlite3_db_path)
    yield conn
    conn.close()


@pytest.fixture
def pg_conn(postgresql):
    """Runs the sqitch plan and loads seed data before returning db connection.
    """
    columns = ["driverref", "number", "code", "forename", "surname", "dob", "nationality", "url"]
    with postgresql:
        # Loads data from f1db fixture data
        with postgresql.cursor() as cur:
            cur.execute(
                """\
                create table drivers (
                  driverid serial not null primary key,
                  driverref varchar(255) not null default '',
                  number integer default null,
                  code varchar(3) default null,
                  forename varchar(255) not null default '',
                  surname varchar(255) not null default '',
                  dob date default null,
                  nationality varchar(255) default null,
                  url varchar(255) not null unique default ''
                );"""
            )
        with postgresql.cursor() as cur:
            with DRIVERS_DATA_PATH.open() as fp:
                cur.copy_from(fp, "drivers", sep=",", columns=columns)
    return postgresql


@pytest.fixture()
def pg_dsn(pg_conn):
    p = pg_conn.get_dsn_parameters()
    return f"postgres://{p['user']}@{p['host']}:{p['port']}/{p['dbname']}"
