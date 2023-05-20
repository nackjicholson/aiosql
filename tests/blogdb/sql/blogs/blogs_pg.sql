-- name: pg-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         to_char(published, 'YYYY-MM-DD HH24:MI') as "published"
    from blogs
    join users using(userid)
   where published >= :published
order by published desc;


-- name: pg-publish-blog<!
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

-- name: pg-no-publish<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where false;

-- name: pg-bulk-publish*!
-- Insert many blogs at once
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
);

-- name: pg-get-modulo$
-- %-escaped percent modulo operator
SELECT :numerator %% :denominator;

-- name: pg-get-modulo-2$
-- no-escape modulo + cast
SELECT :numerator::INT8 % :denominator::INT8;
