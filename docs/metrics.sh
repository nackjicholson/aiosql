#! /bin/bash
#
# count badge metrics
#

echo -n "supported databases: "
python -c "from aiosql.aiosql import _DRIVERS; print(len(_DRIVERS));"

echo -n "supported drivers: "
python -c "from aiosql.aiosql import _ADAPTERS; print(len(_ADAPTERS));"

# NOTE this does only count tests that could run
# pytest --collect-only tests/test_*.py | tail -1
echo -n "all tests: "
egrep '(^def|as) +test_' tests/test_* | wc -l
