-- name: get-all-blogs
select * from blogs;

-- name: publish-blog<!
insert into blogs(userid, title, content) values (:userid, :title, :content);

-- name: insert-many*!
insert into blogs(userid, title, content, published) values (?, ?, ?, ?);


-- name: get_user_blogs
-- Get blogs with a fancy formatted published date
    select b.title,
           strftime('%Y-%m-%d %H:%M', b.published) as published,
           u.username
      from blogs b
inner join users u on b.userid = u.userid
     where u.username = :username
  order by b.published desc;
