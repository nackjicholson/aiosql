import csv
from pathlib import Path

import pytest
from pytest_postgresql import factories as pg_factories
from pytest_mysql import factories as my_factories
import sqlite3
import apsw

import aiosql

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


# test adapter registering and overriding
aiosql.aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)
aiosql.aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)


def pytest_addoption(parser):
    parser.addoption("--postgresql-detached", action="store_true")


def create_user_blogs(db):
    assert db in ("sqlite", "pgsql", "mysql")
    serial = (
        "serial" if db == "pgsql" else "integer" if db == "sqlite" else "integer auto_increment"
    )
    return (
        f"""create table users (
                userid {serial} primary key,
                username text not null,
                firstname text not null,
                lastname text not null);""",
        f"""create table blogs (
                blogid {serial} primary key,
                userid integer not null,
                title text not null,
                content text not null,
                published date not null default (CURRENT_DATE),
                foreign key (userid) references users(userid));""",
    )


def fill_user_blogs(cur, db):
    assert db in ("sqlite", "mysql")
    param = "?" if db == "sqlite" else "%s"
    with USERS_DATA_PATH.open() as fp:
        users = list(csv.reader(fp))
        cur.executemany(
            f"""
               insert into users (
                    username,
                    firstname,
                    lastname
               ) values ({param}, {param}, {param});""",
            users,
        )
    with BLOGS_DATA_PATH.open() as fp:
        blogs = list(csv.reader(fp))
        cur.executemany(
            f"""
                insert into blogs (
                    userid,
                    title,
                    content,
                    published
                ) values ({param}, {param}, {param}, {param});""",
            blogs,
        )


#
# SQLite stuff
#


def populate_sqlite3_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("\n".join(create_user_blogs("sqlite")))
    fill_user_blogs(cur, "sqlite")
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


# FIXME maybe it should look at the connection state?
class APSWConnection(apsw.Connection):
    """APSW Connection wrapper with autocommit off."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._begin()

    def _begin(self):
        self.cursor().execute("BEGIN").close()

    def commit(self):  # pragma: no cover
        self.cursor().execute("COMMIT").close()
        self._begin()

    def _rollback(self):
        self.cursor().execute("ROLLBACK").close()

    def rollback(self):  # pragma: no cover
        self._rollback()
        self._begin()

    def close(self):
        self._rollback()
        super().close()


@pytest.fixture()
def apsw_conn(sqlite3_db_path):
    conn = APSWConnection(sqlite3_db_path)
    yield conn
    conn.close()


#
# Postgres stuff
#

# NOT USED
# postgresqlnoproc = pg_factories.postgresql("postgresql_noproc")


# guess psycopg version
def is_psycopg2(conn):
    return hasattr(conn, "get_dsn_parameters")


@pytest.fixture
def pg_conn(request):
    """Loads seed data before returning db connection."""
    if request.config.getoption("postgresql_detached"):  # pragma: no cover
        conn = request.getfixturevalue("postgresql_noproc")
    else:
        conn = request.getfixturevalue("postgresql")

    # Loads data from blogdb fixture data
    with conn.cursor() as cur:

        for tc in create_user_blogs("pgsql"):
            cur.execute(tc)

        # guess whether we have a psycopg 2 or 3 connection
        with USERS_DATA_PATH.open() as fp:
            if is_psycopg2(conn):  # pragma: no cover
                cur.copy_from(fp, "users", sep=",", columns=["username", "firstname", "lastname"])
            else:
                with cur.copy(
                    "COPY users(username, firstname, lastname) FROM STDIN (FORMAT CSV)"
                ) as cope:
                    cope.write(fp.read())

        with BLOGS_DATA_PATH.open() as fp:
            if is_psycopg2(conn):  # pragma: no cover
                cur.copy_from(
                    fp, "blogs", sep=",", columns=["userid", "title", "content", "published"]
                )
            else:  # assume psycopg 3
                with cur.copy(
                    "COPY blogs(userid, title, content, published) FROM STDIN (FORMAT CSV)"
                ) as cope:
                    cope.write(fp.read())

    conn.commit()

    yield conn


@pytest.fixture()
def pg_params(pg_conn):
    if is_psycopg2(pg_conn):  # pragma: no cover
        dsn = pg_conn.get_dsn_parameters()
        del dsn["tty"]
    else:  # assume psycopg 3.x
        dsn = pg_conn.info.get_parameters()
    return dsn


@pytest.fixture()
def pg_dsn(request, pg_params):
    p = pg_params
    pw = request.config.getoption("postgresql_password")
    yield f"postgres://{p['user']}:{pw}@{p['host']}:{p['port']}/{p['dbname']}"


#
# MySQL stuff
#
# NOTE pytest-mysql does not seem to work with mariadb on my box
#


@pytest.fixture
def my_dsn(mysql_proc):
    mp = mysql_proc
    assert mp.host == "localhost"
    yield {
        "user": mp.user,
        # "password": mp.password,
        "host": mp.host,
        "port": mp.port,
        # "database": mp.dbname,
    }


@pytest.fixture
def my_db(mysql):
    with mysql.cursor() as cur:
        for tc in create_user_blogs("mysql"):
            cur.execute(tc)
        mysql.commit()
        fill_user_blogs(cur, "mysql")
        mysql.commit()
    yield mysql
    # FIXME mysql.commit()
