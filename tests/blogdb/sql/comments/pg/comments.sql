-- name: create-table#
create table comments (
    commentid serial primary key,
    blogid integer not null references blogs(blogid),
    author text not null,
    content text not null
)
