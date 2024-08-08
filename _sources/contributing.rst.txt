Contributing
============

First, thank you for considering to make a contribution to this project.
Spending your valuable time helping make this project better is deeply appreciated.
All kinds of contributions are helpful and welcome.

-  Report issues `<https://github.com/nackjicholson/aiosql/issues>`__
-  Review or make your own pull requests `<https://github.com/nackjicholson/aiosql/pulls>`__
-  Write documentation `<https://github.com/nackjicholson/aiosql/tree/master/docs>`__

Whether you have an idea for a feature improvement or have found a troubling bug, thank you for being here.


Packaging & Distribution
------------------------

This aiosql repository uses the python standard packaging tools.
Read about them in more detail at the following links.

-  `Python Packaging User Guide <https://packaging.python.org/>`__
-  `PyPA - Packaging & Distributing
   projects\* <https://packaging.python.org/guides/distributing-packages-using-setuptools/>`__
-  `setuptools <https://setuptools.readthedocs.io/en/latest/index.html>`__
-  `build <https://pypa-build.readthedocs.io/en/stable/>`__
-  `twine <https://twine.readthedocs.io/en/latest/#configuration>`__


Development Setup
-----------------

1. Create a virtual environment

.. code:: sh

    git clone git@github.com:nackjicholson/aiosql.git
    cd aiosql
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip

All subsequent steps will assume you are using python within your activated virtual environment.

1. Install your environment to the dependencies defined in ``dev-requirements.txt``

Note: different versions of Python may install different versions of dependencies.
As `aiosql` is more or less expected to work with all these module versions, the
bare minimum version pinning is done in the requirements file.

.. code:: sh

    pip install -r dev-requirements.txt

1. Run tests

.. code:: sh

    pytest

Alternatively, there is a `Makefile` to automate some of the above tasks:

.. code:: sh

    make venv.dev  # install dev virtualenv
    source venv/bin/activate
    make check  # run all checks: pytest, black, flake8, coverage…

Also, there is a working `poetry` setup in `pyproject.toml`.


Dependency Management
---------------------

There is no dependency for using ``aiosql``.

For development you need to test with various databases and even more drivers,
see above for generating a working python environment.
