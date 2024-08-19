-- name: sqlite-get-blogs-published-after
-- Get all blogs by all authors published after the given date.
    select b.title,
           u.username,
           strftime('%Y-%m-%d %H:%M', b.published) as published
      from blogs b
inner join users u on b.userid = u.userid
     where b.published >= :published
  order by b.published desc;


-- name: sqlite-bulk-publish*!
-- Insert many blogs at once
insert into blogs (
  userid,
  title,
  content,
  published
)
values (?, ?, ?, ?);

-- name: sqlite-get-modulo$
-- no-escaped percent modulo operator
SELECT :numerator % :denominator;

-- name: publish-a-blog<!
insert into blogs(userid, title, content)
  values (:userid, :title, :content);

-- name: create_schema#
create table users (
    userid integer not null primary key,
    username text not null,
    firstname integer not null,
    lastname text not null
);

create table blogs (
    blogid integer not null primary key,
    userid integer not null,
    title text not null,
    content text not null,
    published date not null default CURRENT_DATE,
    foreign key(userid) references users(userid)
);
