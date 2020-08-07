# Defining SQL Queries

## Query Names

Name definitions are how aiosql determines the name of the methods that SQL code blocks are accessible by. A query name is defined by a SQL comment of the form "-- name: <query-name>".

```sql
-- name: get_all_blogs
select * from blogs;
```

This query will be available in aiosql under the python method name `.get_all_blogs(conn)`

## Query Comments

_./sql/blogs.sql_

```sql
-- name: get_all_blogs
-- Fetch all fields for every blog in the database.
select * from blogs;
```

Any other SQL comments you make between the name definition and your code will be used a the python documentation string for the generated method. You can use `help()` in the Python REPL to view these comments while using python.

```python
Python 3.8.3 (default, May 17 2020, 18:15:42) 
[GCC 10.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import aiosql
>>> queries = aiosql.from_path("sql", "sqlite3")
>>> help(queries.get_all_blogs)
Help on method get_all_blogs in module aiosql.queries:

get_all_blogs(conn, *args, **kwargs) method of aiosql.queries.Queries instance
    Fetch all fields for every blog in the database.
```

## Operators

This section describes the usage of various query operator symbols that you can annotate query names with in order to direct how aiosql will execute and return results.

### No Operator (Default)

In the above [Query Names](#query-names) section the `get-all-blogs` name is written without any trailing operators.

```sql
-- name: get_all_blogs
```

The lack of an operator is actually the most basic operator used by default for your queries. This tells aiosql to execute the query and to return all the results. In the case of `get-all-blogs` that means a `select` statement will be executed and a list of rows will be returned. When writing your application you will often need to perform other operations besides `select`, like `insert`, `delete`, and perhaps bulk operations. The operators detailed in the other sections of this doc let you declare in your SQL code how that query should be executed by a python database driver.

### `^` Select One

The `^` operator executes a query and returns the first row of a result set. When there are no rows in the result set it returns `None`. This is useful when you know there should be one, and exactly one result from your query.

As an example, if you have a unique constraint on the `username` field in your `users` table which makes it impossible for two users to share the same username, you could use `^` to direct aiosql to select a single user rather than a list of rows of length 1.

```sql
-- name: get_user_by_username^
select userid,
       username,
       name
  from users
 where username = :username;
```

When used from Python this query will either return `None` or the singular selected row.

```python
queries.get_user_by_username(conn, username="willvaughn")
# => (1, "willvaughn", "William Vaughn") or None
```

### `!` Insert/Update/Delete

The `!` operator executes SQL without returning any results. It is meant for statements that use `insert`, `update`, and `delete` to make modifications to database rows without a necessary return value.

```sql
-- name: publish_blog!
insert into blogs(userid, title, content) values (:userid, :title, :content);

-- name: remove_blog!
-- Remove a blog from the database
delete from blogs where blogid = :blogid;
```

The methods generated are:

```text
publish_blog(conn, userid: int, title: str, content: str) -> None:
remove_blog(conn, blogid: int) -> None:
```

Each can be called to alter the database, but both will return `None`.

### `<!` Insert/Update/Delete Returning

When performing a modification of rows, or adding new rows, sometimes it is necessary to return values using the `returning` clause where available. With the `<!` operator aiosql can execute a query and return values.

When using SQLite this operator will return the id of the inserted row using [`cur.lastrowid`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.lastrowid).

```sql
-- name: publish_blog<!
insert into blogs(userid, title, content) values (:userid, :title, :content);
```

Executing this query in python will return the `blogid` of the inserted row.

```python
queries = aiosql.from_path("blogs.sql", "sqlite3")
# ... connection code ...
blogid = queries.publish_blog(conn, userid=1, title="Hi" content="blah blah.")
```

PostgreSQL allows returning multiple values via the `returning` clause of queries. This same query using `psycopg2` might look like the following.

```sql
-- name: publish_blog<!
insert into (userid, title, content)
     values (:userid, :title, :content)
  returning blogid, title;
```

In python a tuple is returned with the `blogid` and `title` of the inserted row.

```python
queries = aiosql.from_path("blogs.sql", "psycopg2")
# ... connection code ...
blogid, title = queries.publish_blog(conn, userid=1, title="Hi" content="blah blah.")
```

### `*!` Insert/Update/Delete Many

The `*!` operator directs aiosql to execute a SQL statement over all items of a given sequence. Under the hood this calls the `executemany` method of many database drivers. See [sqlite3 Cursor.executemany](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.executemany) for an example.

In aiosql we can use this for a bulk publish method that operates over a list of blog entries.

```sql
-- name: bulk_publish*!
-- Insert many blogs at once
insert into blogs (userid, title, content, published)
values (:userid, :title, :content, :published);
```

```python
queries = aiosql.from_path("blogs.sql", "psycopg2")
# ... connection code ...
blogs = [
    {"userid": 1, "title": "First Blog", "content": "...", published: datetime(2018, 1, 1)},
    {"userid": 1, "title": "Next Blog", "content": "...", published: datetime(2018, 1, 2)},
    {"userid": 2, "title": "Hey, Hey!", "content": "...", published: datetime(2018, 7, 28)},
]
queries.bulk_publish(conn, blogs)
```

### `#` Execute Scripts

Using this operarator will execute sql statements as a script. You can't do variable substitution with the `#` operator. An example usecase is using data definition statements like create table in order to setup a database.

```sql
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
```

```python
queries = aiosql.from_path("create_schema.sql", "sqlite3")
# ... connection code ...
queries.create_schema(conn)
```
