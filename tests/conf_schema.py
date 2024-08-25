# non portable SQL statements to create, fill and clear the database schema

import csv
from pathlib import Path

# CSV data file paths
BLOGDB_PATH = Path(__file__).parent / "blogdb"
USERS_DATA_PATH = BLOGDB_PATH / "data/users_data.csv"
BLOGS_DATA_PATH = BLOGDB_PATH / "data/blogs_data.csv"


def create_user_blogs(db):
    assert db in ("sqlite", "pgsql", "mysql", "duckdb", "mssql")
    serial = (
        "SERIAL" if db == "pgsql" else
        "INTEGER" if db in ("sqlite", "duckdb") else
        "INTEGER auto_increment" if db == "mysql" else
        "INTEGER IDENTITY(1, 1)" if db == "mssql" else
        f"unexpected db: {db}"
    )
    ifnotexists = "IF NOT EXISTS" if db in ("sqlite", "pgsql", "mysql", "duckdb") else ""
    current_date = "CURRENT_DATE" if db in ("sqlite", "pgsql", "mysql", "duckdb") else "GETDATE()"
    text = "VARCHAR(MAX)" if db == "mssql" else "TEXT"
    ddl_statements = [
        f"""CREATE TABLE {ifnotexists} users (
                userid {serial} PRIMARY KEY,
                username {text} NOT NULL,
                firstname {text} NOT NULL,
                lastname {text} NOT NULL);""",
        f"""CREATE TABLE {ifnotexists} blogs (
                blogid {serial} PRIMARY KEY,
                userid INTEGER NOT NULL,
                title {text} NOT NULL,
                content {text} NOT NULL,
                published DATE NOT NULL DEFAULT ({current_date}),
                FOREIGN KEY (userid) REFERENCES users(userid));""",
    ]
    if db and db == "duckdb":
        ddl_statements.extend(["create sequence users_seq;", "create sequence blogs_seq;"])
    return tuple(ddl_statements)


def drop_user_blogs(db):
    if db == "mssql":
        # yuk, procedural
        return [
            "IF OBJECT_ID('comments', 'U') IS NOT NULL\n\tDROP TABLE comments\n",
            "IF OBJECT_ID('blogs', 'U') IS NOT NULL\n\tDROP TABLE blogs\n",
            "IF OBJECT_ID('users', 'U') IS NOT NULL\n\tDROP TABLE users\n",
        ]
    else:
        return [
            "DROP TABLE IF EXISTS comments",
            "DROP TABLE IF EXISTS blogs",
            "DROP TABLE IF EXISTS users",
        ]


def fill_user_blogs(cur, db):
    # NOTE postgres filling relies on copy
    # NOTE duckdb filling relies on its own functions
    assert db in ("sqlite", "mysql", "mssql")
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
