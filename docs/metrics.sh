#! /bin/bash
#
# count badge metrics
#

ndb=$(python -c "from aiosql.aiosql import _DRIVERS; print(len(_DRIVERS));")
ndr=$(python -c "from aiosql.aiosql import _ADAPTERS; print(len(_ADAPTERS));")
# NOTE this does only count tests that could run
# pytest --collect-only tests/test_*.py | tail -1
nte=$(egrep '(^def|as) +test_' tests/test_* | wc -l)

echo "supported databases: $ndb"
echo "supported drivers: $ndr"
echo "all tests: $nte"

echo "extracts:"
grep "databases-$ndb-info" README.rst
grep "drivers-$ndr-info" README.rst
grep "tests-$nte%" README.rst
