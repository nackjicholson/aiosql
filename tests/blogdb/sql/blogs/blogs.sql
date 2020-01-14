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
  :content,
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


-- name: get-user-blogs-df
-- record_class: UserBlogDF
-- Get blogs authored by a user.
  select title,
         published
    from blogs
   where userid = :userid
order by published desc;
