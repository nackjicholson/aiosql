-- name: create-table-users#
CREATE TABLE IF NOT EXISTS users(
  userid SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
);

-- name: create-table-blogs#
CREATE TABLE IF NOT EXISTS blogs(
  blogid SERIAL PRIMARY KEY,
  userid INTEGER NOT NULL REFERENCES users,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  published DATE NOT NULL DEFAULT CURRENT_DATE
);

-- name: get-blogs-published-after(published)
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         to_char(published, 'YYYY-MM-DD HH24:MI') as "published"
    from blogs
    join users using(userid)
   where published >= :published
order by published desc;


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
)
returning blogid, title;

-- name: no-publish()<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where false;

-- name: bulk-publish(userid, title, content, published)*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
  values (:userid, :title, :content, :published);
