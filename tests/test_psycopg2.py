from datetime import date
from pathlib import Path
from typing import NamedTuple

import aiosql
import psycopg2
import psycopg2.extras
import pytest


class UserBlogSummary(NamedTuple):
    title: str
    published: date


RECORD_CLASSES = {"UserBlogSummary": UserBlogSummary}


@pytest.fixture()
def queries():
    dir_path = Path(__file__).parent / "blogdb" / "sql"
    return aiosql.from_path(dir_path, "psycopg2", RECORD_CLASSES)


def test_record_query(pg_dsn, queries):
    with psycopg2.connect(dsn=pg_dsn, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        actual = queries.users.get_all(conn)

    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


def test_parameterized_query(pg_conn, queries):
    actual = queries.users.get_by_lastname(pg_conn, lastname="Doe")
    expected = [(3, "janedoe", "Jane", "Doe"), (2, "johndoe", "John", "Doe")]
    assert actual == expected


def test_parameterized_record_query(pg_dsn, queries):
    with psycopg2.connect(dsn=pg_dsn, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        actual = queries.blogs.pg_get_blogs_published_after(conn, published=date(2018, 1, 1))

    expected = [
        {"title": "How to make a pie.", "username": "bobsmith", "published": "2018-11-23 00:00"},
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


def test_record_class_query(pg_conn, queries):
    actual = queries.blogs.get_user_blogs(pg_conn, userid=1)
    expected = [
        UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23)),
        UserBlogSummary(title="What I did Today", published=date(2017, 7, 28)),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected

    one = queries.blogs.get_latest_user_blog(pg_conn, userid=1)
    assert one == UserBlogSummary(title="How to make a pie.", published=date(2018, 11, 23))


def test_select_cursor_context_manager(pg_conn, queries):
    with queries.blogs.get_user_blogs_cursor(pg_conn, userid=1) as cursor:
        actual = cursor.fetchall()
        expected = [
            ("How to make a pie.", date(2018, 11, 23)),
            ("What I did Today", date(2017, 7, 28)),
        ]
        assert actual == expected


def test_select_one(pg_conn, queries):
    actual = queries.users.get_by_username(pg_conn, username="johndoe")
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


def test_select_value(pg_conn, queries):
    actual = queries.users.get_count(pg_conn)
    expected = 3
    assert actual == expected


def test_insert_returning(pg_conn, queries):
    with pg_conn:
        blogid, title = queries.blogs.pg_publish_blog(
            pg_conn,
            userid=2,
            title="My first blog",
            content="Hello, World!",
            published=date(2018, 12, 4),
        )
        with pg_conn.cursor() as cur:
            cur.execute(
                """\
                select blogid,
                       title
                  from blogs
                 where blogid = %s;
                """,
                (blogid,),
            )
            expected = cur.fetchone()

    assert (blogid, title) == expected

    with pg_conn:
        res = queries.blogs.pg_no_publish(pg_conn)
        assert res is None


def test_delete(pg_conn, queries):
    # Removing the "janedoe" blog titled "Testing"
    actual = queries.blogs.remove_blog(pg_conn, blogid=2)
    assert actual is None

    janes_blogs = queries.blogs.get_user_blogs(pg_conn, userid=3)
    assert len(janes_blogs) == 0


def test_insert_many(pg_conn, queries):
    blogs = [
        {
            "userid": 2,
            "title": "Blog Part 1",
            "content": "content - 1",
            "published": date(2018, 12, 4),
        },
        {
            "userid": 2,
            "title": "Blog Part 2",
            "content": "content - 2",
            "published": date(2018, 12, 5),
        },
        {
            "userid": 2,
            "title": "Blog Part 3",
            "content": "content - 3",
            "published": date(2018, 12, 6),
        },
    ]

    with pg_conn:
        actual = queries.blogs.pg_bulk_publish(pg_conn, blogs)
        assert actual is None

        johns_blogs = queries.blogs.get_user_blogs(pg_conn, userid=2)
        assert johns_blogs == [
            ("Blog Part 3", date(2018, 12, 6)),
            ("Blog Part 2", date(2018, 12, 5)),
            ("Blog Part 1", date(2018, 12, 4)),
        ]


def test_execute_script(pg_conn, queries):
    with pg_conn:
        actual = queries.comments.pg_create_comments_table(pg_conn)
        assert actual == "CREATE TABLE"
