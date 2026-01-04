-- name: create-table-users#
CREATE TABLE IF NOT EXISTS users(
  userid INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
);
CREATE SEQUENCE users_seq;

-- name: create-table-blogs#
CREATE TABLE IF NOT EXISTS blogs(
  blogid INTEGER PRIMARY KEY,
  userid INTEGER NOT NULL REFERENCES users,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  published DATE NOT NULL DEFAULT (CURRENT_DATE)
);
CREATE SEQUENCE blogs_seq;

-- name: get-blogs-published-after(published)
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           strftime('%Y-%m-%d %H:%M', b.published) as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= :published
  order by b.published desc;


-- name: bulk-publish*!
-- Insert many blogs at once
insert into blogs (
  blogid,
  userid,
  title,
  content,
  published
)
values (nextval('blogs_seq'), ?, ?, ?, ?);

-- name: publish-blog<!
insert into blogs (
  blogid,
  userid,
  title,
  content,
  published
)
values (
  nextval('blogs_seq'), ?, ?, ?, ?
)
returning (blogid, title);

-- name: add_many_blogs*!
INSERT INTO blogs (blogid, userid, title, content, published)
  VALUES (NEXTVAL('blogs_seq'), ?, ?, ?, ?);
