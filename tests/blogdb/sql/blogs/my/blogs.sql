-- name: create-table-users#
CREATE TABLE IF NOT EXISTS users(
  userid INTEGER auto_increment PRIMARY KEY,
  username TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
);

-- name: create-table-blogs#
CREATE TABLE IF NOT EXISTS blogs(
  blogid INTEGER auto_increment PRIMARY KEY,
  userid INTEGER NOT NULL REFERENCES users,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  published DATE NOT NULL DEFAULT (CURRENT_DATE)
);

-- name: get-blogs-published-after(published)
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           DATE_FORMAT(b.published, '%Y-%m-%d %H:%i') as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= :published
  order by b.published desc;


-- name: bulk-publish*!
-- Insert many blogs at once
insert into blogs (
  userid,
  title,
  content,
  published
)
values (%s, %s, %s, %s);

-- name: publish-new-blog(userid, title, content)
insert into blogs (userid, title, content)
  values (:userid, :title, :content)
  returning blogid, title;
