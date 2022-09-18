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
PG_PORT	= 15432
PG_USER	= pytest
PG_PASS	= pytest
PG_DB	= pytest

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
	$(RM) .coverage poetry.lock

clean.venv: clean
	$(RM) -r venv $(MODULE).egg-info

#
# VARIOUS CHECKS
#
.PHONY: check.pytest check.mypy check.flake8 check.black check.coverage check.rstcheck check

check.rstcheck: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	rstcheck docs/source/*.rst

check.pytest: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(PYTEST) $(PYTOPT) tests/

PG_DETACHED	= --postgresql-detached --postgresql-user=$(PG_USER) --postgresql-password=$(PG_PASS) --postgresql-dbname=$(PG_DB) --postgresql-port=$(PG_PORT)

.PHONY: check.pytest.postgres.detached
check.pytest.postgres.detached:
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	$(PYTEST) $(PG_DETACHED) $(PYTOPT) \
	  tests/test_psycopg2.py \
	  tests/test_psycopg3.py \
	  tests/test_pygresql.py \
	  tests/test_pg8000.py \
	  tests/test_asyncpg.py

check.mypy: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	mypy --install-types --non-interactive $(MODULE)

check.flake8: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	flake8 $(MODULE)

check.black: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	black $(MODULE) tests --check

check.coverage: $(VENV)
	[ "$(VENV)" ] && source $(VENV)/bin/activate
	coverage run -m $(PYTEST) $(PYTOPT)
	coverage html
	coverage report --fail-under=100 --include='$(MODULE)/*'

check: check.pytest check.mypy check.flake8 check.black check.coverage check.rstcheck

#
# testing with docker
#

.docker.mysql: dockerfile.mysql
	docker build -f dockerfile.mysql -t aiosql-mysql-test .
	touch $@

.docker.mariadb: dockerfile.mariadb
	docker build -f dockerfile.mariadb -t aiosql-mariadb-test .
	touch $@

.docker.pytest.mysql: .docker.mysql
	docker run -v "$$PWD:/app:ro" \
	  -e MYSQL_ALLOW_EMPTY_PASSWORD=1 aiosql-mysql-test \
	  make -f /app/Makefile PYTOPT="-k my" .docker.pytest

.PHONY: .docker.pytest.mariadb
.docker.pytest.mariadb: .docker.mariadb
	docker run -v "$$PWD:/app:ro" \
	  -e MARIADB_ALLOW_EMPTY_PASSWORD=1 aiosql-mariadb-test \
	  make -f /app/Makefile PYTOPT="-k maria" .docker.pytest

.docker.run.postgres:
	docker run -d --name aiosql-pytest-postgres \
	  -p $(PG_PORT):5432 \
	  -e POSTGRES_USER=$(PG_USER) \
	  -e POSTGRES_PASSWORD=$(PG_PASS) \
	  -e POSTGRES_DB=$(PG_DB) \
	  postgres
	touch $@

.PHONY: docker.pytest.postgres
docker.pytest.postgres: .docker.run.postgres
	$(MAKE) check.pytest.postgres.detached

.PHONY: docker.stop
docker.stop:
	docker stop aiosql-pytest-postgres
	$(RM) .docker.run.postgres

# run inside docker image
.docker.pytest:
	test -d /app -a -d /home/calvin/app -a -d /venv || exit 1
	cp -r /app/. /home/calvin/app/.
	/venv/bin/pip install .
	$(MAKE) VENV=/venv check.pytest

#
# PYPI PUBLICATION
#

dist:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: publish
publish: dist check
	echo "# run twine to publish on pypi"
	echo twine upload --repository $(MODULE) dist/*
