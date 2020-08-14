-- name: get-record-by-username^
-- record_class: UserSummary
select userid,
       username,
       firstname,
       lastname
  from users
 where username = :username;
