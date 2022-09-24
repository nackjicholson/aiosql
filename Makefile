#
# Convenient Makefile to help with development.
#
# Try `make help` for help.
#

MODULE	= aiosql

SHELL	= /bin/bash
.ONESHELL:

PYTHON	= python
PYTEST	= pytest --log-level=debug --capture=tee-sys --asyncio-mode=auto
PYTOPT	=

VENV	= venv
PIP		= venv/bin/pip

# docker
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
	echo " - check: run all above checks"
	echo " - publish: publish a new release on pypi (for maintainers)"

#
# VIRTUAL ENVIRONMENT
#
# NOTE: pinning module versions is somehow counter productive because we really
# want to work with multiple versions of python, which all have their own
# requirements and dependencies and random incompatibilities wrt libraries,
# so the result is kind of a mess, so we attempt at doing nearly nothing and
# hope for the bese, i.e. dependencies will not break the library.
#
.PHONY: venv.dev venv.prod venv.last

venv:
	$(PYTHON) -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .

venv.dev: venv
	$(PIP) install -r dev-requirements.txt

venv.prod: venv

venv.last:
	$(PIP) install $$($(PIP) freeze | cut -d= -f1 | grep -v -- '^-e') -U

#
# CLEANUP
#
.PHONY: clean clean.venv

clean:
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf
	$(RM) -r dist build .mypy_cache .pytest_cache htmlcov .docker.*
	$(RM) .coverage .coverage.* poetry.lock

clean.venv: clean
	$(RM) -r venv $(MODULE).egg-info

INSTALL	= $(VENV)/.aiosql_installed

$(INSTALL):
	$(VENV)/bin/pip install -e .
	touch $@

#
# VARIOUS CHECKS
#
.PHONY: check.rstcheck
check.rstcheck: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	rstcheck docs/source/*.rst

.PHONY: check.pytest
check.pytest: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(PYTEST) $(PYTOPT) tests/

# FIXME this cannot work because of unexpected pytest options
# .PHONY: check.pytest.detached
# check.pytest.detached: \
# 	check.pytest.misc \
# 	check.pytest.postgres.detached \
# 	check.pytest.mysql.detached \
# 	check.pytest.mariadb.detached

.PHONY: check.mypy
check.mypy: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	mypy --install-types --non-interactive $(MODULE)

.PHONY: check.flake8
check.flake8: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	flake8 $(MODULE)

.PHONY: check.black
check.black: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	black $(MODULE) tests --check

.PHONY: check.coverage
check.coverage: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	coverage run -m $(PYTEST) $(PYTOPT) tests/
	coverage html
	coverage report --fail-under=100 --include='$(MODULE)/*'

.PHONY: check
check: check.pytest check.mypy check.flake8 check.black check.coverage check.rstcheck

#
# docker utils
#

PG_DETACHED	= \
	--postgresql-detached \
	--postgresql-host=$(PG_HOST) \
	--postgresql-port=$(PG_PORT) \
	--postgresql-user=$(PG_USER) \
	--postgresql-password=$(PG_PASS) \
	--postgresql-dbname=$(PG_NAME)

.PHONY: check.pytest.postgres.detached
check.pytest.postgres.detached: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	./tests/wait.py $(PG_HOST) $(PG_PORT) 5
	$(PYTEST) $(PG_DETACHED) $(PYTOPT) \
	  tests/test_psycopg2.py \
	  tests/test_psycopg3.py \
	  tests/test_pygresql.py \
	  tests/test_pg8000.py \
	  tests/test_asyncpg.py

MY_DETACHED	= \
	--mysql-detached \
	--mysql-host=$(MY_HOST) \
	--mysql-port=$(MY_PORT) \
	--mysql-user=$(MY_USER) \
	--mysql-passwd=$(MY_PASS) \
	--mysql-dbname=$(MY_NAME)

.PHONY: check.pytest.mysql.detached
check.pytest.mysql.detached: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	# FIXME this does not seem to work…
	./tests/wait.py $(MY_HOST) $(MY_PORT) 10
	# run with all 3 drivers
	$(PYTEST) $(MY_DETACHED) $(PYTOPT) \
	  --mysql-driver=MySQLdb tests/test_mysqldb.py
	$(PYTEST) $(MY_DETACHED) $(PYTOPT) \
	  --mysql-driver=pymysql tests/test_pymysql.py
	$(PYTEST) $(MY_DETACHED) $(PYTOPT) \
	  --mysql-driver=mysql.connector tests/test_myco.py

MA_DETACHED	= \
	--mysql-detached \
	--mysql-host=$(MA_HOST) \
	--mysql-port=$(MA_PORT) \
	--mysql-user=$(MA_USER) \
	--mysql-passwd=$(MA_PASS) \
	--mysql-dbname=$(MA_NAME)

.PHONY: check.pytest.mariadb.detached
check.pytest.mariadb.detached: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	./tests/wait.py $(MA_HOST) $(MA_PORT) 5
	$(PYTEST) $(MA_DETACHED) $(PYTOPT) \
	  --mysql-driver=mariadb tests/test_mariadb.py

.PHONY: check.pytest.misc
check.pytest.misc: $(INSTALL)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(PYTEST) $(PYTOPT) \
	  tests/test_loading.py \
	  tests/test_patterns.py \
	  tests/test_sqlite3.py \
	  tests/test_apsw.py \
	  tests/test_aiosqlite.py

# coverage by overriding PYTEST

# -a: append
# -p: parallel
COVERAGE	= $(VENV)/bin/coverage run -p

.PHONY: check.coverage.postgres.detached
check.coverage.postgres.detached: PYTEST=$(COVERAGE) -m pytest
check.coverage.postgres.detached: check.pytest.postgres.detached

.PHONY: check.coverage.mysql.detached
check.coverage.mysql.detached: PYTEST=$(COVERAGE) -m pytest
check.coverage.mysql.detached: check.pytest.mysql.detached

.PHONY: check.coverage.mariadb.detached
check.coverage.mariadb.detached: PYTEST=$(COVERAGE) -m pytest
check.coverage.mariadb.detached: check.pytest.mariadb.detached

.PHONY: check.coverage.misc
check.coverage.misc: PYTEST=$(COVERAGE) -m pytest
check.coverage.misc: check.pytest.misc

.PHONY: docker.pytest
docker.pytest:
	$(MAKE) -C docker $@

.PHONY: docker.coverage
docker.coverage:
	$(MAKE) -C docker $@
	# $(COVERAGE) combine

# start docker servers for local tests
.docker.run.postgres:
	docker run -d --name aiosql-pytest-postgres \
	  -p $(PG_PORT):5432 \
	  -e POSTGRES_USER=$(PG_USER) \
	  -e POSTGRES_PASSWORD=$(PG_PASS) \
	  -e POSTGRES_DB=$(PG_NAME) \
	  postgres
	sleep 5
	touch $@

.docker.run.mysql:
	docker run -d --name aiosql-pytest-mysql \
	  -p $(MY_PORT):3306 \
	  -e MYSQL_ROOT_PASSWORD=$(MY_PASS) \
	  -e MYSQL_USER=$(MY_USER) \
	  -e MYSQL_PASSWORD=$(MY_PASS) \
	  -e MYSQL_DATABASE=$(MY_NAME) \
	  mysql
	sleep 5
	touch $@

.docker.run.mariadb:
	docker run -d --name aiosql-pytest-mariadb \
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
	docker stop aiosql-pytest-postgres aiosql-pytest-mysql aiosql-pytest-mariadb || exit 0
	$(RM) .docker.run.*

#
# PYPI PUBLICATION
#

dist:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: publish
publish: dist check
	echo "# run twine to publish on pypi"
	echo twine upload --repository $(MODULE) dist/*
