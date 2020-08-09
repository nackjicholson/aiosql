from pathlib import Path

import aiosql
import pytest

from conftest import UserBlogSummary


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@pytest.fixture()
def queries(record_classes):
    p = Path(__file__).parent / "blogdb" / "sql"
    return aiosql.from_path(p, "sqlite3", record_classes)


def test_record_query(sqlite3_conn, queries):
    sqlite3_conn.row_factory = dict_factory
    actual = queries.users.get_all(sqlite3_conn)

    assert len(actual) == 3
    assert actual[0] == {
        "userid": 1,
        "username": "bobsmith",
        "firstname": "Bob",
        "lastname": "Smith",
    }


def test_parameterized_query(sqlite3_conn, queries):
    actual = queries.users.get_by_lastname(sqlite3_conn, lastname="Doe")
    expected = [(3, "janedoe", "Jane", "Doe"), (2, "johndoe", "John", "Doe")]
    assert actual == expected


def test_parameterized_record_query(sqlite3_conn, queries):
    sqlite3_conn.row_factory = dict_factory
    actual = queries.blogs.sqlite_get_blogs_published_after(sqlite3_conn, published="2018-01-01")

    expected = [
        {"title": "How to make a pie.", "username": "bobsmith", "published": "2018-11-23 00:00"},
        {"title": "Testing", "username": "janedoe", "published": "2018-01-01 00:00"},
    ]

    assert actual == expected


def test_record_class_query(sqlite3_conn, queries):
    actual = queries.blogs.get_user_blogs(sqlite3_conn, userid=1)
    expected = [
        UserBlogSummary(title="How to make a pie.", published="2018-11-23"),
        UserBlogSummary(title="What I did Today", published="2017-07-28"),
    ]

    assert all(isinstance(row, UserBlogSummary) for row in actual)
    assert actual == expected


def test_select_cursor_context_manager(sqlite3_conn, queries):
    with queries.blogs.get_user_blogs_cursor(sqlite3_conn, userid=1) as cursor:
        actual = cursor.fetchall()
        expected = [("How to make a pie.", "2018-11-23"), ("What I did Today", "2017-07-28")]
        assert actual == expected


def test_select_one(sqlite3_conn, queries):
    actual = queries.users.get_by_username(sqlite3_conn, username="johndoe")
    expected = (2, "johndoe", "John", "Doe")
    assert actual == expected


def test_insert_returning(sqlite3_conn, queries):
    with sqlite3_conn:
        blogid = queries.blogs.publish_blog(
            sqlite3_conn,
            userid=2,
            title="My first blog",
            content="Hello, World!",
            published="2018-12-04",
        )
    cur = sqlite3_conn.cursor()
    cur.execute(
        """\
        select title
          from blogs
         where blogid = ?;
    """,
        (blogid,),
    )
    actual = cur.fetchone()
    cur.close()
    expected = ("My first blog",)

    assert actual == expected


def test_delete(sqlite3_conn, queries):
    # Removing the "janedoe" blog titled "Testing"
    actual = queries.blogs.remove_blog(sqlite3_conn, blogid=2)
    assert actual is None

    janes_blogs = queries.blogs.get_user_blogs(sqlite3_conn, userid=3)
    assert len(janes_blogs) == 0


def test_insert_many(sqlite3_conn, queries):
    blogs = [
        (2, "Blog Part 1", "content - 1", "2018-12-04"),
        (2, "Blog Part 2", "content - 2", "2018-12-05"),
        (2, "Blog Part 3", "content - 3", "2018-12-06"),
    ]

    with sqlite3_conn:
        actual = queries.blogs.sqlite_bulk_publish(sqlite3_conn, blogs)
        assert actual is None

        johns_blogs = queries.blogs.get_user_blogs(sqlite3_conn, userid=2)
        assert johns_blogs == [
            ("Blog Part 3", "2018-12-06"),
            ("Blog Part 2", "2018-12-05"),
            ("Blog Part 1", "2018-12-04"),
        ]
