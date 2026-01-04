-- name: create-table-users#
CREATE TABLE users(
  userid INTEGER IDENTITY(1, 1) PRIMARY KEY,
  username VARCHAR(MAX) NOT NULL,
  firstname VARCHAR(MAX) NOT NULL,
  lastname VARCHAR(MAX) NOT NULL
);

-- name: create-table-blogs#
CREATE TABLE blogs(
  blogid INTEGER IDENTITY(1, 1) PRIMARY KEY,
  userid INTEGER NOT NULL REFERENCES users,
  title VARCHAR(MAX) NOT NULL,
  content VARCHAR(MAX) NOT NULL,
  published DATE NOT NULL DEFAULT (GETDATE())
);

-- name: drop-table-comments#
IF OBJECT_ID('comments', 'U') IS NOT NULL
  DROP TABLE comments;

-- name: drop-table-blogs#
IF OBJECT_ID('blogs', 'U') IS NOT NULL
  DROP TABLE blogs;

-- name: drop-table-users#
IF OBJECT_ID('users', 'U') IS NOT NULL
  DROP TABLE users;

-- name: get-blogs-published-after(published)
-- Get all blogs by all authors published after the given date.
  select title,
         username,
         concat(convert(VARCHAR, published, 23), ' 00:00') as "published"
    from blogs as b
    join users as u ON (u.userid = b.userid)
   where published >= :published
order by published desc;


-- name: publish-blog(userid, title, content, published)<!
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
  :content,
  :published
);

-- name: no-publish()<!
-- Test an hypothetical empty returning clause
select blogid, title
from blogs
where 0 = 1;

-- name: bulk-publish(userid, title, content, published)*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
  values (:userid, :title, :content, :published);
