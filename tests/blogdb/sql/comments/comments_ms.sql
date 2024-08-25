-- name: ms-create-comments-table#
create table comments (
    commentid integer identity(1, 1) primary key,
    blogid integer not null references blogs(blogid),
    author varchar(255) not null,
    content text not null
)
