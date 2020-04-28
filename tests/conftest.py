import csv
import sqlite3
from pathlib import Path
from typing import NamedTuple

import pytest

BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


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


@pytest.fixture
def pg_conn(postgresql):
    """Runs the sqitch plan and loads seed data before returning db connection.
    """
    with postgresql:
        # Loads data from blogdb fixture data
        with postgresql.cursor() as cur:
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

        with postgresql.cursor() as cur:
            with USERS_DATA_PATH.open() as fp:
                cur.copy_from(fp, "users", sep=",", columns=["username", "firstname", "lastname"])
            with BLOGS_DATA_PATH.open() as fp:
                cur.copy_from(
                    fp, "blogs", sep=",", columns=["userid", "title", "content", "published"]
                )

    return postgresql


@pytest.fixture()
def pg_dsn(pg_conn):
    p = pg_conn.get_dsn_parameters()
    return f"postgres://{p['user']}@{p['host']}:{p['port']}/{p['dbname']}"


class UserBlogSummary(NamedTuple):
    title: str
    published: str


@pytest.fixture
def _record_classes():
    return {"UserBlogSummary": UserBlogSummary}


@pytest.fixture(params=["class", "import_path"])
def record_classes(request, _record_classes):
    if request.param == "class":
        return _record_classes

    elif request.param == "import_path":
        return {
            name: f"{klass.__module__}.{klass.__name__}" for name, klass in _record_classes.items()
        }

    raise RuntimeError("Unknown record_class type")
