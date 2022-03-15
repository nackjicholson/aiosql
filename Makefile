#
# Convenient Makefile to help with development.
#
# Try `make help` for help.
#

SHELL	= /bin/bash
.ONESHELL:

PYTHON	= python
PYTEST	= pytest --log-level=debug --capture=tee-sys
PYTOPT	=

VENV	= venv
PIP		= venv/bin/pip

.PHONY: help
help:
	@echo "useful targets:"
	echo " - help: show this help"
	echo " - venv: generate python virtual environment directory"
	echo " - venv.dev: make venv suitable for development"
	echo " - venv.prod: make venv suitable for production"
	echo " - venv.last: fill venv with latests packages"
	echo " - dev-requirements.txt: regenerate this file from *.in"
	echo " - clean: clean up various generated files and directories"
	echo " - clean.venv: also remove the venv directory"
	echo " - check.pytest: run pytest tests"
	echo " - check.mypy: run mypy type checker"
	echo " - check.flake8: run flake8 code style checks"
	echo " - check.black: run black formatter checks"
	echo " - check: run all above checks"
	echo " - coverage: generate html coverage report"

#
# VIRTUAL ENVIRONMENT
#
.PHONY: venv.dev venv.prod venv.last

venv:
	$(PYTHON) -m venv venv
	$(PIP) install pip-tools

venv.dev: venv
	$(PIP)-sync dev-requirements.txt

venv.prod: venv
	$(PIP)-sync requirements.txt

venv.last:
	$(PIP) install $$($(PIP) freeze | cut -d= -f1 | grep -v -- '^-e') -U

dev-requirements.txt: dev-requirements.in venv
	$(PIP)-compile $<

#
# CLEANUP
#
.PHONY: clean clean.venv

clean:
	$(RM) -r __pycache__ */__pycache__ */*/__pycache__ *.egg-info dist build .mypy_cache .pytest_cache htmlcov
	$(RM) .coverage

clean.venv: clean
	$(RM) -r venv

#
# VARIOUS CHECKS
#
.PHONY: check.pytest check.mypy check.flake8 check.black check coverage

check.pytest: $(VENV)
	source venv/bin/activate
	$(PYTEST) $(PYTOPT) tests/

check.mypy: $(VENV)
	source venv/bin/activate
	mypy aiosql

check.flake8: $(VENV)
	source venv/bin/activate
	flake8 aiosql

check.black: $(VENV)
	source venv/bin/activate
	black aiosql tests --check

check: check.pytest check.mypy check.flake8 check.black

coverage: $(VENV)
	source venv/bin/activate
	coverage run -m $(PYTEST) $(PYTOPT)
	coverage html
