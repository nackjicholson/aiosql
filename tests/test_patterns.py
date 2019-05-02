from aiosql.patterns import var_pattern


def test_var_pattern_is_quote_aware():
    sql = """
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
    groupdicts = [m.groupdict() for m in var_pattern.finditer(sql)]
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


def test_var_pattern_does_not_drop_semicolon():
    """Make sure keywords ending queries are recognized even without
    semi-colons.
    """
    sql = """
        select a,
               b,
               c
          FROM foo
         WHERE a = :a"""

    groupdicts = [m.groupdict() for m in var_pattern.finditer(sql)]
    assert len(groupdicts) == 1

    expected = {"dblquote": None, "lead": " ", "quote": None, "trail": "", "var_name": "a"}
    assert groupdicts[0] == expected
