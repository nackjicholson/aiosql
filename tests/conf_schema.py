import csv
from pathlib import Path

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


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
