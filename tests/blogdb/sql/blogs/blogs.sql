-- this part before the first description
is expected
TO BE IGNORED SILENTLY…

-- name: drop-table-users#
DROP TABLE IF EXISTS users;

-- name: drop-table-blogs#
DROP TABLE IF EXISTS blogs;

-- name: drop-table-comments#
DROP TABLE IF EXISTS comments;

-- name: get-all-blogs()
-- Fetch all fields for every blog in the database.
select * from blogs;

-- name: publish-blog(userid, title, content, published)<!
insert into blogs (
  userid,
  title,
  content,
  published
)
values (
  :userid,
  :title,
  :content,
  :published
);

-- name: remove-blog(blogid)!
-- Remove a blog from the database
delete from blogs where blogid = :blogid;

-- name: get-user-blogs(userid)
-- record_class: UserBlogSummary
-- Get blogs authored by a user.
  select title AS title,
         published AS published
    from blogs
   where userid = :userid
order by published desc;


-- name: get-latest-user-blog(userid)^
-- record_class: UserBlogSummary
-- Get latest blog by user.
select title AS title, published AS published
from blogs
where userid = :userid
order by published desc
limit 1;

-- name: search(title, published)
select title from blogs where title LIKE :title and published = :published;

-- name: blog_title(blogid)^
select blogid, title from blogs where blogid = :blogid;

-- name: with-params(name, x)^
select length(:name), :x.real + x.imaj;

-- name: new-blog(userid, title, content)!
insert into blogs (userid, title, content)
  values (:userid, :title, :content);

-- name: publish-new-blog(userid, title, content)$
insert into blogs (userid, title, content)
  values (:userid, :title, :content)
  returning blogid;

-- name: add_many_blogs*!
INSERT INTO blogs (userid, title, content, published)
  VALUES (%s, %s, %s, %s);
