-- name: get_all_greetings
-- Get all the greetings in the database
select greeting_id, greeting
  from greetings
 order by 1;

-- name: get_user_by_username^
-- Get a user from the database using a named parameter
select user_id, username, name
  from users
  where username = :username;
