Contributing
============

First, thank you for considering to make a contribution to this project.
Spending your valuable time helping make this project better is deeply appreciated.
All kinds of contributions are helpful and welcome.

-  Report issues `<https://github.com/nackjicholson/aiosql/issues>`__
-  Review or make your own pull requests `<https://github.com/nackjicholson/aiosql/pulls>`__
-  Write documentation `<https://github.com/nackjicholson/aiosql/tree/main/docs/source>`__

Whether you have an idea for a feature improvement or have found a troubling bug, thank you for being here.


Packaging & Distribution
------------------------

This aiosql repository uses the Python standard packaging tools.
Read about them in more detail at the following links.

-  `Python Packaging User Guide <https://packaging.python.org/>`__
-  `PyPA - Packaging & Distributing projects <https://packaging.python.org/guides/distributing-packages-using-setuptools/>`__
-  `setuptools <https://setuptools.readthedocs.io/en/latest/index.html>`__
-  `build <https://pypa-build.readthedocs.io/en/stable/>`__
-  `twine <https://twine.readthedocs.io/en/latest/#configuration>`__

Development Setup
-----------------

1. Create a virtual environment

.. code:: sh

    # get the project sources
    git clone git@github.com:nackjicholson/aiosql.git
    cd aiosql
    # create a venv manually
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip

All subsequent steps will assume you are using python within your activated virtual environment.

1. Install the development dependencies

As a development library, aiosql is expected to work with all supported
versions of Python, and many drivers.
The bare minimum of version pinning is declared in the dependencies.

.. code:: sh

    # development tools
    pip install .[dev]
    # per-database stuff
    pip install .[dev-sqlite]
    pip install .[dev-postgres]
    pip install .[dev-duckdb]
    pip install .[dev-mysql]
    pip install .[dev-mariadb]

1. Run tests

.. code:: sh

    pytest

Alternatively, there is a convenient ``Makefile`` to automate the above tasks:

.. code:: sh

    make venv.dev  # install dev virtual environment
    source venv/bin/activate
    make check  # run all checks: pytest, flake8, coverage…

Also, there is a working ``poetry`` setup in ``pyproject.toml``.

Dependency Management
---------------------

There is no dependency for using ``aiosql`` other than installing your
driver of choice.

For development you need to test with various databases and even more drivers,
see above for generating a working python environment.

See also the ``docker`` sub-directory which contains dockerfiles for testing
with Postgres, MySQL, MariaDB and MS SQL Server.
