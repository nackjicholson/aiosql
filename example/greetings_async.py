import asyncio
import aiosql
import aiosqlite

queries = aiosql.from_path("greetings.sql", "aiosqlite")

async def main():
    # Parallel queries!!!
    async with aiosqlite.connect("greetings.db") as conn:
        greetings, user = await asyncio.gather(
            queries.get_all_greetings(conn),
            queries.get_user_by_username(conn, username="willvaughn")
        )

        for _, greeting in greetings:
            print(f"{greeting}, {user[2]}!")

asyncio.run(main())
