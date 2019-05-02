-- name: insert_many*!
insert into users(username, firstname, lastname) values (?, ?, ?);


-- name: get_all
-- record_class: User
select userid,
       username,
       firstname,
       lastname
  from users;
