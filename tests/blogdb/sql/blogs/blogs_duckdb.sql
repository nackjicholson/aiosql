-- name: duckdb-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           strftime('%Y-%m-%d %H:%M', b.published) as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= :published
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
returning (blogid, title);
