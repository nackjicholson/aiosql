import aiosql
import sqlite3

queries = aiosql.from_path("greetings.sql", "sqlite3")

with sqlite3.connect("greetings.db") as conn:
    user = queries.get_user_by_username(conn, username="willvaughn")
    # user: (1, "willvaughn", "William")

    for _, greeting in queries.get_all_greetings(conn):
        # scan: (1, "Hi"), (2, "Aloha"), (3, "Hola"), …
        print(f"{greeting}, {user[2]}!")
    # Hi, William!
    # Aloha, William!
    # …
