-- name: get-blogs-published-after
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         concat(convert(VARCHAR, published, 23), ' 00:00') as "published"
    from blogs as b
    join users as u ON (u.userid = b.userid)
   where published >= :published
order by published desc;


-- name: publish-blog<!
insert into blogs (
  userid,
  title,
  content,
  published
)
output inserted.blogid, inserted.title
values (
  :userid,
  :title,
  :contents,
  :published
);

-- name: no-publish<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where 0 = 1;

-- name: bulk-publish*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
  values (:userid, :title, :contents, :published);
