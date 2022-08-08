DROP TABLE IF EXISTS greetings;
DROP TABLE IF EXISTS users;

CREATE TABLE greetings(
    greeting_id INTEGER PRIMARY KEY,
    greeting TEXT NOT NULL
);

INSERT INTO greetings(greeting_id, greeting) VALUES
  (1, 'Hi'),
  (2, 'Aloha'),
  (3, 'Hola'),
  (4, 'Bonjour'),
  (5, '你好');

CREATE TABLE users(
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

INSERT INTO users(user_id, username, name) VALUES
  (1, 'willvaughn', 'William'),
  (2, 'calvin', 'Fabien');
