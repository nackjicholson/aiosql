-- name: get-blogs-published-after
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         to_char(published, 'YYYY-MM-DD HH24:MI') as "published"
    from blogs
    join users using(userid)
   where published >= :published
order by published desc;


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
returning blogid, title;

-- name: no-publish<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where false;

-- name: bulk-publish*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
  values (:userid, :title, :contents, :published);
