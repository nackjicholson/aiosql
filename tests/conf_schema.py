import csv
from pathlib import Path

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


def create_user_blogs(db):
    assert db in ("sqlite", "pgsql", "mysql")
    serial = (
        "SERIAL" if db == "pgsql" else "INTEGER" if db == "sqlite" else "INTEGER auto_increment"
    )
    return (
        f"""CREATE TABLE IF NOT EXISTS users (
                userid {serial} PRIMARY KEY,
                username TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL);""",
        f"""CREATE TABLE IF NOT EXISTS blogs (
                blogid {serial} PRIMARY KEY,
                userid INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                published DATE NOT NULL DEFAULT (CURRENT_DATE),
                FOREIGN KEY (userid) REFERENCES users(userid));""",
    )


def drop_user_blogs(db):
    return (
        f"DROP TABLE IF EXISTS comments",
        f"DROP TABLE IF EXISTS blogs",
        f"DROP TABLE IF EXISTS users",
    )


def fill_user_blogs(cur, db):
    # NOTE postgres filling relies on copy
    assert db in ("sqlite", "mysql")
    param = "?" if db == "sqlite" else "%s"
    with USERS_DATA_PATH.open() as fp:
        users = list(csv.reader(fp))
        cur.executemany(
            f"""
               INSERT INTO users (
                    username,
                    firstname,
                    lastname
               ) VALUES ({param}, {param}, {param});""",
            users,
        )
    with BLOGS_DATA_PATH.open() as fp:
        blogs = list(csv.reader(fp))
        cur.executemany(
            f"""
                INSERT INTO blogs (
                    userid,
                    title,
                    content,
                    published
                ) VALUES ({param}, {param}, {param}, {param});""",
            blogs,
        )
