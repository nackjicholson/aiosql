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

.PHONY: help
help:
	@echo "useful targets:"
	echo " - help: show this help"
	echo " - venv: generate python virtual environment directory"
	echo " - dev-requirements.txt: regenerate this file from *.in"
	echo " - clean: clean up various generated files and directories"
	echo " - clean.venv: also remove the venv directory"
	echo " - check.pytest: run pytest"
	echo " - check.mypy: run mypy"
	echo " - check.flake8: run flake8"
	echo " - check: run all above checks"
	echo " - coverage: generate html coverage report"

venv:
	$(PYTHON) -m venv venv
	source venv/bin/activate
	pip install pip-tools
	pip-sync dev-requirements.txt

dev-requirements.txt: dev-requirements.in venv
	source venv/bin/activate
	pip-compile $<

.PHONY: clean clean.venv
clean:
	$(RM) -r __pycache__ */__pycache__ *.egg-info dist build .mypy_cache .pytest_cache htmlcov
	$(RM) .coverage

clean.venv: clean
	$(RM) -r venv

.PHONY: check.pytest check.mypy check.flake8 check coverage
check.pytest: venv
	source venv/bin/activate
	$(PYTEST) $(PYTOPT) tests/

check.mypy: venv
	source venv/bin/activate
	mypy aiosql

check.flake8: venv
	source venv/bin/activate
	flake8 aiosql

check: check.pytest check.mypy check.flake8

coverage: venv
	source venv/bin/activate
	coverage run -m $(PYTEST) $(PYTOPT)
	coverage html
