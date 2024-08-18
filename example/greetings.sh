#! /bin/bash

echo "# creating sqlite greetings database…"
sqlite3 greetings.db < greetings_create.sql

echo "# running standard aiosql example code…"
python greetings.py

echo "# running async aiosql example code…"
python greetings_async.py

echo "# running cursor aiosql example code…"
python greetings_cursor.py

echo "# running execute values and observer…"
python observe_query.py

echo "# removing greetings database."
rm greetings.db
