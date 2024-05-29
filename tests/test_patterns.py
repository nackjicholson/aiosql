import pytest
from aiosql.utils import VAR_REF
from aiosql.query_loader import _UNCOMMENT, _remove_ml_comments

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
            "dquote": None,
            "lead": None,
            "squote": "'YYYY-MM-DD\"T\"HH24:MI:SSOF'",
            "var_name": None,
        },
        {
            "dquote": None,
            "lead": " ",
            "squote": None,
            "var_name": "created_at_mark",
        },
        {"dquote": None, "lead": " ", "squote": None, "var_name": "foo_mark"},
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

    expected = {"dquote": None, "lead": " ", "squote": None, "var_name": "a"}
    assert groupdicts[0] == expected


def test_var_pattern_handles_empty_sql_string_literals():
    """Make sure SQL '' are treated correctly and don't cause a substitution to be skipped."""
    sql = r"""
        select blah
          from foo
         where lower(regexp_replace(blah,'\\W','','g')) = lower(regexp_replace(:blah,'\\W','','g'));"""

    groupdicts = [m.groupdict() for m in VAR_REF.finditer(sql)]

    expected_single_quote_match = {
        "dquote": None,
        "lead": None,
        "squote": "''",
        "var_name": None,
    }
    assert groupdicts[1] == expected_single_quote_match

    expected_var_match = {
        "dquote": None,
        "lead": "(",
        "squote": None,
        "var_name": "blah",
    }
    assert groupdicts[3] == expected_var_match


# must remove *only* OK comments
COMMENTED = """
KO
-- KO
/* OK */
'/* KO */'
"/* KO */"
' /* KO
   */'
" /* KO
   */"
/*
 * OK
 */
-- /* KO
-- KO */
/* OK
  -- OK
  ' OK ' "OK "
 */
KO
/* OK */ -- KO 'KO'
-- KO */
/*+ KO (hints must be kept!) */
"""


def test_comments():
    n = 0
    for ma in _UNCOMMENT.finditer(COMMENTED):
        matches = ma.groupdict()
        s, d, c, m = matches["squote"], matches["dquote"], matches["oneline"], matches["multiline"]
        # assert s or d or c or m, f"bad match: {m} {matches}"
        if s or d or c or m:
            n += 1
            if m:
                assert "OK" in m and "KO" not in m
            if s:
                assert "KO" in s and "OK" not in s
            if d:
                assert "KO" in d and "OK" not in d
            if c:
                assert "KO" in c and "OK" not in c
    assert n == 13


COMMENT_UNCOMMENT = [
    ("", ""),
    ("hello", "hello"),
    ("world!\n", "world!\n"),
    ("/**/", ""),
    ("/*+ hint */", "/*+ hint */"),
    ("x/*\n*/y\n", "xy\n"),
    ("-- /* */\n", "-- /* */\n"),
    ("-- /* */", "-- /* */"),
    ("'/* */'", "'/* */'"),
    ("--\n/* */X\n", "--\nX\n"),
]


def test_uncomment():
    n = 0
    for c, u in COMMENT_UNCOMMENT:
        n += 1
        assert _remove_ml_comments(c) == u
    assert n == len(COMMENT_UNCOMMENT)
