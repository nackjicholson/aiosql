-- SQL COMMENT THAT SHOULD BE ALLOWED
-- WAS BREAKING IN THIS ISSUE https://github.com/nackjicholson/aiosql/issues/35

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


-- name: search
-- The reason firstname has a :title param is because this is used in a test
-- for a bug in from https://github.com/nackjicholson/aiosql/issues/51
-- There needs to be a duplicate variable name within a duplicate function,
-- "search" in this case across two different sql files. The blogs.sql has
-- another function "search" with a :title key as well.
select username from users where firstname = :title and lastname = :lastname;
