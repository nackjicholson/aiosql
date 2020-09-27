-- name: get-all
-- Get all user records
select * from users;


-- name: get-by-username^
select userid,
       username,
       firstname,
       lastname
  from users
 where username = :username;


-- name: get-by-lastname
  select userid,
         username,
         firstname,
         lastname
    from users
   where lastname = :lastname
order by username asc;


-- name: get-all-sorted
-- Get all user records sorted by username
select * from users order by username asc;


-- name: get-count$
-- Get number of users
select count(*) from users;
