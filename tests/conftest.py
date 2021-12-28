import csv
import sqlite3
from pathlib import Path

import pytest
from pytest_postgresql import factories

BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


def pytest_addoption(parser):
    parser.addoption("--postgresql-detached", action="store_true")


def populate_sqlite3_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
            create table users (
                userid integer not null primary key,
                username text not null,
                firstname integer not null,
                lastname text not null
            );

            create table blogs (
                blogid integer not null primary key,
                userid integer not null,
                title text not null,
                content text not null,
                published date not null default CURRENT_DATE,
                foreign key(userid) references users(userid)
            );
            """
    )

    with USERS_DATA_PATH.open() as fp:
        users = list(csv.reader(fp))
        cur.executemany(
            """
               insert into users (
                    username,
                    firstname,
                    lastname
               ) values (?, ?, ?);""",
            users,
        )
    with BLOGS_DATA_PATH.open() as fp:
        blogs = list(csv.reader(fp))
        cur.executemany(
            """
                insert into blogs (
                    userid,
                    title,
                    content,
                    published
                ) values (?, ?, ?, ?);""",
            blogs,
        )

    conn.commit()
    conn.close()


@pytest.fixture()
def sqlite3_db_path(tmpdir):
    db_path = str(Path(tmpdir.strpath) / "blogdb.db")
    populate_sqlite3_db(db_path)
    return db_path


@pytest.fixture()
def sqlite3_conn(sqlite3_db_path):
    conn = sqlite3.connect(sqlite3_db_path)
    yield conn
    conn.close()


postgresqlnoproc = factories.postgresql("postgresql_noproc")

def is_psycopg2(conn):
    return hasattr(conn, "get_dsn_parameters")

@pytest.fixture
def pg_conn(request):
    """Loads seed data before returning db connection."""
    if request.config.getoption("postgresql_detached"):
        conn = request.getfixturevalue("postgresqlnoproc")
    else:
        conn = request.getfixturevalue("postgresql")

    with conn:
        # Loads data from blogdb fixture data
        with conn.cursor() as cur:
            cur.execute(
                """
                create table users (
                    userid serial not null primary key,
                    username varchar(32) not null,
                    firstname varchar(255) not null,
                    lastname varchar(255) not null
                );"""
            )
            cur.execute(
                """
                create table blogs (
                    blogid serial not null primary key,
                    userid integer not null references users(userid),
                    title varchar(255) not null,
                    content text not null,
                    published date not null default CURRENT_DATE
                );"""
            )

        # guess whether we have a psycopg 2 or 3 connection
        with conn.cursor() as cur:
            if is_psycopg2(conn):
                with USERS_DATA_PATH.open() as fp:
                    cur.copy_from(fp, "users", sep=",", columns=["username", "firstname", "lastname"])
                with BLOGS_DATA_PATH.open() as fp:
                    cur.copy_from(
                        fp, "blogs", sep=",", columns=["userid", "title", "content", "published"]
                    )
            else:  # assume psycopg 3
                import psycopg as pg
                fn = pg.sql.Literal(str(USERS_DATA_PATH)).as_string(None)
                cur.copy(f"COPY users FROM {fn} FORMAT CSV");
                fn = pg.sql.Literal(str(BLOGS_DATA_PATH)).as_string(None)
                cur.copy(f"COPY blogs FROM {fn} FORMAT CSV");

    return conn


@pytest.fixture()
def pg_dsn(request, pg_conn):
    if is_psycopg2(pg_conn):
        p = pg_conn.get_dsn_parameters()
    else:  # assume psycopg 3
        p = pg_conn.info.get_parameters()
    pw = request.config.getoption("postgresql_password")
    return f"postgres://{p['user']}:{pw}@{p['host']}:{p['port']}/{p['dbname']}"
