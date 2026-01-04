-- name: get-all()
-- MS SQL Server does not do an implicit "AS" on *
select
    userid as userid,
    username as username,
    firstname as firstname,
    lastname as lastname
from users
order by 1;

-- name: get-by-username(username)^
select userid as userid,
       username as username,
       firstname as firstname,
       lastname as lastname
  from users
 where username = :username;
