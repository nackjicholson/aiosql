-- name: ms-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         concat(convert(VARCHAR, published, 23), ' 00:00') as "published"
    from blogs as b
    join users as u ON (u.userid = b.userid)
   where published >= :published
order by published desc;


-- name: ms-publish-blog<!
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

-- name: ms-no-publish<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where 0 = 1;

-- name: ms-bulk-publish*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
  values (:userid, :title, :contents, :published);

-- name: ms-get-modulo$
-- %-escaped percent modulo operator
SELECT :numerator %% :denominator;

-- name: ms-get-modulo-2$
-- no-escape modulo + cast
SELECT :numerator::INT8 % :denominator::INT8;
