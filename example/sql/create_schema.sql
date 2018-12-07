-- name: create-schema#
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
