-- name: duckdb-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           strftime('%Y-%m-%d %H:%M', b.published) as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= $published
  order by b.published desc;


-- name: duckdb-bulk-publish*!
-- Insert many blogs at once
insert into blogs (
  blogid,
  userid,
  title,
  content,
  published
)
values (nextval('blogs_seq'), ?, ?, ? , ?);

-- name: duckdb-get-modulo$
-- no-escaped percent modulo operator
SELECT ? % ?;


-- name: duckdb-publish-blog<!
insert into blogs (
  blogid,
  userid,
  title,
  content,
  published
)
values (
  nextval('blogs_seq'), ?, ?, ? , ?
)
returning blogid, title;

-- name: duckdb-remove-blog!
-- Remove a blog from the database
delete from blogs where blogid = $blogid;


-- name: duckdb-get-user-blogs
-- record_class: UserBlogSummary
-- Get blogs authored by a user.
  select title,
         published
    from blogs
   where userid = $userid
order by published desc;


-- name: duckdb-get-latest-user-blog^
-- record_class: UserBlogSummary
-- Get latest blog by user.
select title, published
from blogs
where userid = $userid
order by published desc
limit 1;


-- name: duckdb-search
select title from blogs where title = $title and published = $published;


-- name: duckdb-square$
select $val::int * $val::int as squared;


-- name: duckdb-blog_title^
select blogid, title from  blogs where blogid=$blogid;
