-- name: create-table#
create table comments (
    commentid integer primary key auto_increment,
    blogid integer not null,
    author text not null,
    content text not null,
    foreign key(blogid) references blogs(blogid)
);
