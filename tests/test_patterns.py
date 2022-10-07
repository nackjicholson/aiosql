import pytest
from aiosql.utils import VAR_REF

pytestmark = [
    pytest.mark.misc,
]


def test_var_pattern_is_quote_aware():
    sql = r"""
          select foo_id,
                 bar_id,
                 to_char(created_at, 'YYYY-MM-DD"T"HH24:MI:SSOF')
            from foos
            join bars using(bar_id)
            join bazs using(baz_id)
           where created_at < :created_at_mark
             and foo_mark > :foo_mark
        order by created_at desc, source_name asc;
    """
    groupdicts = [m.groupdict() for m in VAR_REF.finditer(sql)]
    assert len(groupdicts) == 3

    expected = [
        {
            "dblquote": None,
            "lead": None,
            "quote": "'YYYY-MM-DD\"T\"HH24:MI:SSOF'",
            "trail": None,
            "var_name": None,
        },
        {
            "dblquote": None,
            "lead": " ",
            "quote": None,
            "trail": "\n",
            "var_name": "created_at_mark",
        },
        {"dblquote": None, "lead": " ", "quote": None, "trail": "\n", "var_name": "foo_mark"},
    ]
    assert groupdicts == expected


def test_var_pattern_does_not_require_semicolon_trail():
    """Make sure keywords ending queries are recognized even without
    semi-colons.
    """
    sql = r"""
        select a,
               b,
               c
          FROM foo
         WHERE a = :a"""

    groupdicts = [m.groupdict() for m in VAR_REF.finditer(sql)]
    assert len(groupdicts) == 1

    expected = {"dblquote": None, "lead": " ", "quote": None, "trail": "", "var_name": "a"}
    assert groupdicts[0] == expected


def test_var_pattern_handles_empty_sql_string_literals():
    """Make sure SQL '' are treated correctly and don't cause a substitution to be skipped."""
    sql = r"""
        select blah
          from foo
         where lower(regexp_replace(blah,'\\W','','g')) = lower(regexp_replace(:blah,'\\W','','g'));"""

    groupdicts = [m.groupdict() for m in VAR_REF.finditer(sql)]

    expected_single_quote_match = {
        "dblquote": None,
        "lead": None,
        "quote": "''",
        "trail": None,
        "var_name": None,
    }
    assert groupdicts[1] == expected_single_quote_match

    expected_var_match = {
        "dblquote": None,
        "lead": "(",
        "quote": None,
        "trail": ",",
        "var_name": "blah",
    }
    assert groupdicts[3] == expected_var_match
