#
# Convenient Makefile to help with development.
#
# Try `make help` for help.
#

MODULE	= aiosql

SHELL	= /bin/bash
.ONESHELL:

PYTHON	= python
LOGLVL	= info
PYTEST	= pytest --log-level=$(LOGLVL) --capture=tee-sys --asyncio-mode=auto
PYTOPT	=

VENV	= venv
PIP		= pip
WAIT	= ./tests/wait.py

# docker settings
PG_HOST	= localhost
PG_PORT	= 15432
PG_USER	= pytest
PG_PASS	= pytest
PG_NAME	= pytest

MY_HOST	= localhost
MY_PORT	= 13306
MY_USER	= pytest
MY_PASS	= pytest
MY_NAME	= pytest

MA_HOST	= localhost
MA_PORT	= 23306
MA_USER	= pytest
MA_PASS	= pytest
MA_NAME	= pytest

.PHONY: help
help:
	@echo "useful targets:"
	echo " - help: show this help"
	echo " - venv: generate python virtual environment directory"
	echo " - venv.dev: make venv suitable for development"
	echo " - venv.prod: make venv suitable for production"
	echo " - venv.last: fill venv with latests packages"
	echo " - clean: clean up various generated files and directories"
	echo " - clean.venv: also remove the venv directory"
	echo " - check.pytest: run pytest tests"
	echo " - check.mypy: run mypy type checker"
	echo " - check.flake8: run flake8 code style checks"
	echo " - check.black: run black formatter checks"
	echo " - check.coverage: run coverage and generate html report"
	echo " - check.rstcheck: check rest files"
	echo " - check: run all above checks"
	echo " - publish: publish a new release on pypi (for maintainers)"

#
# VIRTUAL ENVIRONMENT
#
# NOTE: pinning module versions is somehow counter productive because we really
# want to work with multiple versions of python, which all have their own
# requirements and dependencies and random incompatibilities wrt libraries,
# so the result is kind of a mess, so we attempt at doing nearly nothing and
# hope for the best, i.e. dependencies will not break the library.
#
.PHONY: venv.dev venv.prod venv.last

venv:
	$(PYTHON) -m venv venv
	source venv/bin/activate
	$(PIP) install --upgrade pip

venv.dev: venv
	source venv/bin/activate
	$(PIP) install .[dev,dev-postgres,dev-sqlite,dev-duckdb]

venv.dist: venv
	source venv/bin/activate
	$(PIP) install .[dist]

venv.prod: venv

venv.last: venv
	source venv/bin/activate
	$(PIP) install $$($(PIP) freeze | cut -d= -f1 | grep -v -- '^-e') -U

# direct module installation for github or docker
ifdef VENV
PIP		= $(VENV)/bin/pip
INSTALL	= $(VENV)/.aiosql_installed
else
INSTALL = .aiosql_installed
endif

$(INSTALL): $(VENV)
	$(PIP) install -e .
	touch $@

#
# CLEANUP
#
.PHONY: clean clean.venv

clean:
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf
	$(RM) -r dist build .mypy_cache .pytest_cache htmlcov .docker.* $(MODULE).egg-info docs/build docs/html
	$(RM) .coverage .coverage.* poetry.lock
	$(MAKE) -C docker clean

clean.venv: clean
	$(RM) -r venv $(MODULE).egg-info

#
# VARIOUS CHECKS
#
# the targets below are expected to work more or less for:
# - local tests (pytest managed instances)
# - local docker tests (docker servers, local client)
# - full docker tests (docker servers and clients)
# - github tests
#
.PHONY: check.mypy
check.mypy: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	mypy --install-types --non-interactive $(MODULE)

.PHONY: check.pyright
check.pyright: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	pyright $(MODULE)

.PHONY: check.flake8
check.flake8: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	flake8 $(MODULE)

.PHONY: check.black
check.black: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	black $(MODULE) tests --check

.PHONY: check.rstcheck
check.rstcheck: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	rstcheck --ignore-directives=toctree --ignore-roles=doc,ref docs/source/*.rst

.PHONY: check.pytest
check.pytest: check.pytest.local

# mysql or mariadb
MYSQL	= mysql

.PHONY: check.pytest.local
check.pytest.local: check.pytest.misc check.pytest.postgres.local check.pytest.$(MYSQL).local

.PHONY: check.coverage
check.coverage: check.coverage.local

.PHONY: check
check: check.pytest check.mypy check.flake8 check.black check.coverage check.rstcheck

#
# pytest/coverage local/detached tests
#
check.pytest.%.detached: $(INSTALL)

check.pytest.%.local: WAIT=:
check.pytest.%.local: $(VENV)

#
# Postgres
#

PG_DETACHED	= \
	--postgresql-detached \
	--postgresql-host=$(PG_HOST) \
	--postgresql-port=$(PG_PORT) \
	--postgresql-user=$(PG_USER) \
	--postgresql-password=$(PG_PASS) \
	--postgresql-dbname=$(PG_NAME)

.PHONY: check.pytest.postgres.detached
check.pytest.postgres.detached: PYTOPT+=$(PG_DETACHED)
check.pytest.postgres.detached: check.pytest.postgres

.PHONY: check.pytest.postgres.local
check.pytest.postgres.local: check.pytest.postgres

.PHONY: check.pytest.postgres
check.pytest.postgres: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(WAIT) $(PG_HOST) $(PG_PORT) 5 || exit 0
	$(PYTEST) $(PYTOPT) \
	  tests/test_psycopg2.py \
	  tests/test_psycopg3.py \
	  tests/test_pygresql.py \
	  tests/test_pg8000.py \
	  tests/test_asyncpg.py

#
# MySQL
#

.PHONY: check.pytest.mysql.local
check.pytest.mysql.local: check.pytest.mysql

MY_DETACHED	= \
	--mysql-detached \
	--mysql-tries=10 \
	--mysql-host=$(MY_HOST) \
	--mysql-port=$(MY_PORT) \
	--mysql-user=$(MY_USER) \
	--mysql-passwd=$(MY_PASS) \
	--mysql-dbname=$(MY_NAME)

.PHONY: check.pytest.mysql.detached
check.pytest.mysql.detached: PYTOPT+=$(MY_DETACHED)
check.pytest.mysql.detached: check.pytest.mysql

.PHONY: check.pytest.mysql
check.pytest.mysql: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	# FIXME this does not seem to work…
	$(WAIT) $(MY_HOST) $(MY_PORT) 10 || exit 0
	set -e
	# run with all 3 drivers
	$(PYTEST) $(PYTOPT) --mysql-driver=MySQLdb tests/test_mysqldb.py
	$(PYTEST) $(PYTOPT) --mysql-driver=pymysql tests/test_pymysql.py
	$(PYTEST) $(PYTOPT) --mysql-driver=mysql.connector tests/test_myco.py

.PHONY: check.pytest.skip.local
check.pytest.skip.local:
	# skip

#
# MariaDB
#

.PHONY: check.pytest.mariadb.local
check.pytest.mariadb.local: check.pytest.mariadb

MA_DETACHED	= \
	--mysql-detached \
	--mysql-tries=2 \
	--mysql-host=$(MA_HOST) \
	--mysql-port=$(MA_PORT) \
	--mysql-user=$(MA_USER) \
	--mysql-passwd=$(MA_PASS) \
	--mysql-dbname=$(MA_NAME)

.PHONY: check.pytest.mariadb.detached
check.pytest.mariadb.detached: PYTOPT+=$(MA_DETACHED)
check.pytest.mariadb.detached: check.pytest.mariadb

.PHONY: check.pytest.mariadb
check.pytest.mariadb: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(WAIT) $(MA_HOST) $(MA_PORT) 5 || exit 0
	$(PYTEST) $(PYTOPT) --mysql-driver=mariadb tests/test_mariadb.py

#
# SQLite3, DuckDB and Misc
#

.PHONY: check.pytest.misc
check.pytest.misc: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(PYTEST) $(PYTOPT) \
	  tests/test_loading.py \
	  tests/test_patterns.py \
	  tests/test_sqlite3.py \
	  tests/test_apsw.py \
	  tests/test_aiosqlite.py \
	  tests/test_duckdb.py

# run coverage by overriding PYTEST

COVERAGE	= coverage
# parallel runs need a merge afterwards
COVER_RUN	= $(COVERAGE) run -p

check.coverage.%: PYTEST=$(COVER_RUN) -m pytest

.PHONY: check.coverage.postgres.detached
check.coverage.postgres.detached: check.pytest.postgres.detached

.PHONY: check.coverage.postgres.local
check.coverage.postgres.local: check.pytest.postgres.local

.PHONY: check.coverage.mysql.detached
check.coverage.mysql.detached: check.pytest.mysql.detached

.PHONY: check.coverage.mysql.local
check.coverage.mysql.local: check.pytest.mysql.local

.PHONY: check.coverage.mariadb.detached
check.coverage.mariadb.detached: check.pytest.mariadb.detached

.PHONY: check.coverage.mariadb.local
check.coverage.mariadb.local: check.pytest.mariadb.local

.PHONY: check.coverage.skip.local
check.coverage.skip.local:
	# skipped!

.PHONY: check.coverage.misc
check.coverage.misc: check.pytest.misc

.PHONY: check.coverage.local
check.coverage.local: check.coverage.misc check.coverage.postgres.local check.coverage.$(MYSQL).local
	$(MAKE) check.coverage.combine

IS_DOCKER	=

.PHONY: check.coverage.combine
check.coverage.combine: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(COVERAGE) combine
	if [[ "$(IS_DOCKER)" ]] ; then
	  sqlite3 .coverage "UPDATE File SET path=REPLACE(path, '/code/', '$$PWD/')"
	else
	  $(COVERAGE) html
	fi
	$(COVERAGE) report --show-missing --precision=1 --fail-under=100.0 --include='$(MODULE)/*'

#
# Docker runs
#

.PHONY: docker.pytest
docker.pytest:
	$(MAKE) -C docker $@

.PHONY: docker.coverage
docker.coverage:
	$(MAKE) -C docker $@
	$(MAKE) IS_DOCKER=1 check.coverage.combine

# start docker servers for local detached tests
.docker.run.postgres:
	docker run -d --name aiosql-tests-postgres \
	  -p $(PG_PORT):5432 \
	  -e POSTGRES_USER=$(PG_USER) \
	  -e POSTGRES_PASSWORD=$(PG_PASS) \
	  -e POSTGRES_DB=$(PG_NAME) \
	  postgres
	sleep 5
	touch $@

.docker.run.mysql:
	docker run -d --name aiosql-tests-mysql \
	  -p $(MY_PORT):3306 \
	  -e MYSQL_ROOT_PASSWORD=$(MY_PASS) \
	  -e MYSQL_USER=$(MY_USER) \
	  -e MYSQL_PASSWORD=$(MY_PASS) \
	  -e MYSQL_DATABASE=$(MY_NAME) \
	  mysql
	sleep 5
	touch $@

.docker.run.mariadb:
	docker run -d --name aiosql-tests-mariadb \
	  -p $(MA_PORT):3306 \
	  -e MYSQL_ROOT_PASSWORD=$(MA_PASS) \
	  -e MYSQL_USER=$(MA_USER) \
	  -e MYSQL_PASSWORD=$(MA_PASS) \
	  -e MYSQL_DATABASE=$(MA_NAME) \
	  mariadb
	sleep 5
	touch $@

.PHONY: check.pytest.docker.postgres
check.pytest.docker.postgres: .docker.run.postgres
	$(MAKE) check.pytest.postgres.detached

.PHONY: check.pytest.docker.mysql
check.pytest.docker.mysql: .docker.run.mysql
	$(MAKE) check.pytest.mysql.detached

.PHONY: check.pytest.docker.mariadb
check.pytest.docker.mariadb: .docker.run.mariadb
	$(MAKE) check.pytest.mariadb.detached

# FIXME?
.PHONY: check.pytest.docker
check.pytest.docker:
	$(MAKE) check.pytest.misc
	$(MAKE) check.pytest.docker.postgres
	$(MAKE) check.pytest.docker.mysql
	$(MAKE) check.pytest.docker.mariadb
	$(MAKE) docker.stop

.PHONY: docker.stop
docker.stop:
	docker stop aiosql-tests-postgres aiosql-tests-mysql aiosql-tests-mariadb || exit 0
	$(RM) .docker.run.*

#
# PYPI PUBLICATION
#

dist: venv.dist
	source venv/bin/activate
	$(PYTHON) -m build

check.publish: dist
	twine check dist/*

.PHONY: publish
publish: dist
	echo "# run twine to publish on pypi"
	echo twine upload dist/*
