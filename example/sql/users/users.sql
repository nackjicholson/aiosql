-- name: insert-many*!
insert into users(username, firstname, lastname) values (?, ?, ?);


-- name: get-all
select username,
       firstname,
       lastname
  from users;
