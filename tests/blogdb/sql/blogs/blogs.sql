-- this part before the first description
is expected
TO BE IGNORED SILENTLY…

-- name: publish-blog<!
insert into blogs (
  userid,
  title,
  content,
  published
)
values (
  :userid,
  :title,
  :contents,
  :published
)

-- name: remove-blog!
-- Remove a blog from the database
delete from blogs where blogid = :blogid;


-- name: get-user-blogs
-- record_class: UserBlogSummary
-- Get blogs authored by a user.
  select title,
         published
    from blogs
   where userid = :userid
order by published desc;


-- name: get-latest-user-blog^
-- record_class: UserBlogSummary
-- Get latest blog by user.
select title, published
from blogs
where userid = :userid
order by published desc
limit 1;


-- name: search
select title from blogs where title = :title and published = :published;


-- name: square$
select :val::int * :val::int as squared;


-- name: blog_title^
select blogid, title from blogs where blogid = :blogid;
