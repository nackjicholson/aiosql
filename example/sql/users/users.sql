-- name: insert_many*!
insert into users(username, firstname, lastname) values (?, ?, ?);


-- name: get_all
select userid,
       username,
       firstname,
       lastname
  from users;
