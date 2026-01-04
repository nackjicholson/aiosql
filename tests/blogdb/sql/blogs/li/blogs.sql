-- name: create-table-users#
CREATE TABLE IF NOT EXISTS users(
  userid INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
);

-- name: create-table-blogs#
CREATE TABLE IF NOT EXISTS blogs(
  blogid INTEGER PRIMARY KEY,
  userid INTEGER NOT NULL REFERENCES users,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  published DATE NOT NULL DEFAULT (CURRENT_DATE)
);

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
  userid,
  title,
  content,
  published
)
values (?, ?, ?, ?);

-- name: publish-a-blog(userid, title, content)<!
insert into blogs(userid, title, content)
  values (:userid, :title, :content);

-- name: create_schema#
create table users (
    userid integer primary key,
    username text not null,
    firstname integer not null,
    lastname text not null
);

create table blogs (
    blogid integer primary key,
    userid integer not null,
    title text not null,
    content text not null,
    published date not null default CURRENT_DATE,
    foreign key(userid) references users(userid)
);

-- name: add_many_blogs*!
-- NOTE same as bulk-publish
INSERT INTO blogs (userid, title, content, published)
  VALUES (?, ?, ?, ?);
