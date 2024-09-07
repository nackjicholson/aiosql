-- name: add_many_users*!
INSERT INTO users(userid, username, firstname, lastname)
VALUES (NEXTVAL('users_seq'), ?, ?, ?);
