-- name: my-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           DATE_FORMAT(b.published, '%Y-%m-%d %H:%M') as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= :published
  order by b.published desc;


-- name: my-bulk-publish*!
-- Insert many blogs at once
insert into blogs (
  userid,
  title,
  content,
  published
)
values (%s, %s, %s, %s);
