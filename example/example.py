import os
import argparse
import sqlite3

import aiosql


queries = aiosql.from_path("sql", "sqlite3")


def createdb():
    conn = sqlite3.connect("exampleblog.db")
    with conn:
        queries.create_schema(conn)
    conn.close()


def deletedb():
    print("deleting the exampleblog.db file")
    if os.path.exists("exampleblog.db"):
        os.remove("exampleblog.db")


def add_users():
    conn = sqlite3.connect("exampleblog.db")
    users = [("bobsmith", "Bob", "Smith"), ("johndoe", "John", "Doe"), ("janedoe", "Jane", "Doe")]
    with conn:
        queries.users.insert_many(conn, users)
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    createdb_parser = subparsers.add_parser("createdb")
    createdb_parser.set_defaults(cmd=createdb)

    deletedb_parser = subparsers.add_parser("deletedb")
    deletedb_parser.set_defaults(cmd=deletedb)

    add_users_parser = subparsers.add_parser("add-users")
    add_users_parser.set_defaults(cmd=add_users)

    args = parser.parse_args()
    cmd_kwargs = {k: v for k, v in vars(args).items() if k != "cmd"}
    args.cmd(**cmd_kwargs)
