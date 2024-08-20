AioSQL - Versions
=================

TODO
----

- maintain up-to-date wrt Python moving target…
- once 3.9 support is dropped, remove old-style type hints.
- write a small SQLite3-based tutorial?
- tests with other database and drivers?
- allow to pass parameters to connection, cursor…
- rethink classes?

11.1 on 2024-08-20
------------------

- improve documentation.
- upgrade sphinx and corresponding read-the-doc theme.

11.0 on 2024-08-17
------------------

- update and improve documentation.
- do not allow to override existing queries, as it can lead to hard to
  understand bugs.
- use ``pytest.fail`` instead of ``assert False`` in tests.

10.4 on 2024-08-08
------------------

- add history of version changes in the documentation (this file!).
- improve comments and doc strings.

10.3 on 2024-08-03
------------------

- add *Python 3.13* and *PyPy 3.10*

10.2 on 2024-05-29
------------------

- exclude SQL hints from pattern matching on C comments.
- improve tests about SQL comments.

10.1 on 2024-03-06
------------------

- drop ``black`` and ``flake8`` checks, add ``ruff`` instead.
- upgrade doc build GitHub CI version.

10.0 on 2024-03-02
------------------

- add ``:object.attribute`` support to reference object attributes in queries.
- add tests about these with dataclasses.

9.5 on 2024-02-18
-----------------

- add ``duckdb`` support for *Python 3.12* CI.

9.4 on 2024-01-28
-----------------

- upgrade non regression tests CI version.
- improve coverage test report.
- add doc strings to more methods.
- add ``kwargs*only`` option to fail on simple args.
- add relevant tests about previous item.
- move various utils in ``Queries``.
- add more or improve static typing hints.
- minor style changes.

9.3 on 2024-01-18
-----------------

- add pyright check.
- improve generic adapter.
- improve static typing.

9.2 on 2023-12-24
-----------------

- improve some tests.
- minor improvements for async adapters.

9.1 on 2023-12-06
-----------------

- add *Python 3.12* to GitHub CI.
- get release number from package meta data.
- update doc relating to ``<!`` which is not really needed anymore.

9.0 on 2023-07-12
-----------------

- change ``master`` to ``main``.
- update rest files to please pypi checks.
- removing non working *Python 3.12dev* support.
- add ``duckdb`` support.
- rework tests so that they are more homogeneous.

8.0 on 2023-03-18
-----------------

- warn on non ascii characters.
- make select a generator.
- driver ``apsw`` now uses the generic adapter.
- move log to utils.
- support multiline comments by removing them.
- improve docker tests.

7.2 on 2023-01-08
-----------------

- fix regex matching to avoid overlaps.
- improve tests about database-specific quoting and escaping.
- drop not always working re2 dependency.

7.1 on 2022-11-11
-----------------

- add preliminary *Python 3.12* tests.
- improve docker scripts

7.0 on 2022-10-27
-----------------

- use make to run CI tests instead of replicating commands.
- official *Python 3.11* support.
- add rest file check.
- improve test Makefile.
- support *Pytest 7*.
- add docker tests.
- improve documentation.
- rework and refactot tests.
- add mariadb official support.

6.5 on 2022-10-07
-----------------

- refactor code with ``utils.py``.
- use re2 if available.

6.4 on 2022-09-06
-----------------

- add rest checks.
- refactor some code.
- ignore SQL file headers.
- improve debugging experience by locating issues.

6.3 on 2022-08-29
-----------------

- fix the BSD license info.
- improve and actually test readme examples.

6.2 on 2022-08-08
-----------------

- accept mixed case adapter names.
- improve tests.

6.1 on 2022-07-31
-----------------

- add *Python 3.11* preliminary tests.
- upgrade GitHub CI action versions.
- rename pg adapter as pyformat adapter.

6.0 on 2022-07-29
-----------------

- improve makefile resilience.
- add workaround adapter for MySQL.
- use re2 if available.
- simplify requirements, a library should not care too much about versions!
- improve documentation editing.
- add plenty badges to have plenty colors when displaying the readme.
- improve ``pyproject.toml`` file.
- improve tests.
- add ``pygresql`` driver support.

5.0 on 2022-07-23
-----------------

- add flake8 linting to GitHub CI.
- improve makefile.
- use plain methods instead of static methods.
- add ``pg8000`` driver support.

4.0 on 2022-07-10
-----------------

- simplify version numbering to 2 digit.
- add *Python 3.10* support.
- add convenient makefile.
- refactor adapters.
- add ``apsw`` driver support.
- add MySQL support with several drivers.
- test names with dash (``-``).
- refactor and improve tests to reduce code duplications.

3.4.1 on 2022-01-30
-------------------

- use a set of names to simplify code.
- fix some typos.
- add more tests.

3.4.0 on 2021-12-24
-------------------

- use inspect to extract function signature.
- add more tests.

3.3.1 on 2021-07-24
-------------------

- add doc link to setup file.

3.3.0 on 2021-07-23
-------------------

- add package build script.
- add TODO in comments.
- add more tests.
- add relative directory path to query name.

3.2.1 on 2021-07-18
-------------------

- add doc generation script.
- drop travis, add GitHub CI.
- simplify code.
- refactor documentation.
- change build to basic setup.
- add ``setup.cfg`` file.

3.2.0 on 2020-09-26
-------------------

- add selecting a value (``$``) and associated tests.

3.1.3 on 2020-09-26
-------------------

- fix type hints.
- improve testing with Postgres.

3.1.2 on 2020-08-11
-------------------

- add ``mypy`` check.
- add more type and ignore hints.

3.1.1 on 2020-08-09
-------------------

- improve travis CI.
- improve and cleanup documentation for mkdocs instead of sphinx.
- add tests about trailing spaces.

3.1.0 on 2020-07-08
-------------------

- test with *Postgres 12* and *Python 3.6* to *3.8*.
- add loading tests.

3.0.0 on 2019-08-26
-------------------

- add support for ``record_class``.
- improve documentation.
- add some typing.
- add selecting just one row (``^``).
- add tests.
- add some code documentation.
- code refactoring.
- remove explicit ``register_driver_adapter`` and accept any factory instead.
- improve doc examples.
- drop tox support.

2.0.3 on 2018-12-10
-------------------

- fix async adapter issues.

2.0.2 on 2018-12-08
-------------------

- minor code cleanup.

2.0.1 on 2018-12-08
-------------------

- drop link to unmaintained anosql project.
- improve documentation.

2.0.0 on 2018-12-07
-------------------

- adaptater refactoring, including breaking changes.
- add ``_cursor`` variants for full control.
- remove some stuff
