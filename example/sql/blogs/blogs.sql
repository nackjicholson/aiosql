-- name: get-all-blogs
select * from blogs;

-- name: insert-many*!
insert into blogs(userid, title, content, published) values (?, ?, ?, ?);


-- name: get_user_blogs
    select b.title,
           strftime('%Y-%m-%d %H:%M', b.published) as published,
           u.username
      from blogs b
inner join users u on b.userid = u.userid
     where u.username = :username
  order by b.published desc;
