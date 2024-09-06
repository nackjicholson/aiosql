-- name: add_many_users*!
INSERT INTO users(username, firstname, lastname) VALUES (?, ?, ?);
