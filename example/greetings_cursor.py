import asyncio
import aiosql
import aiosqlite
from typing import List

queries = aiosql.from_path("greetings.sql", "aiosqlite")

async def access_cursor():
    async with aiosqlite.connect("greetings.db") as conn:
        # append _cursor after query name
        async with queries.get_all_greetings_cursor(conn) as cur:
            print([col_info[0] for col_info in cur.description])
            first_row = await cur.fetchone()
            all_data = await cur.fetchall()
            print(f"FIRST ROW: {first_row}")  # tuple of first row data
            print(f"OTHER DATA: {all_data}")    # remaining rows

asyncio.run(access_cursor())

# ['greeting_id', 'greeting']
# FIRST ROW: (1, 'Hi')
# OTHER DATA: [(2, 'Aloha'), (3, 'Hola'), (4, 'Bonjour'), (5, '你好')]
