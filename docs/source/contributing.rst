Contributing
============

First, thank you for considering to make a contribution to this project. Spending your valuable time helping make this project better is deeply appreciated. All kinds of contributions are helpful and welcome.

-  Report issues `<https://github.com/nackjicholson/aiosql/issues>`__
-  Review or make your own pull requests `<https://github.com/nackjicholson/aiosql/pulls>`__
-  Write documentation `<https://github.com/nackjicholson/aiosql/tree/master/docs>`__

Whether you have an idea for a feature improvement or have found a troubling bug, thank you for being here.

Packaging & Distribution
------------------------

This aiosql repository uses the python standard packaging tools. Read about them in more detail at the following links.

-  `Python Packaging User Guide <https://packaging.python.org/>`__
-  `PyPA - Packaging & Distributing
   projects\* <https://packaging.python.org/guides/distributing-packages-using-setuptools/>`__
-  `setuptools <https://setuptools.readthedocs.io/en/latest/index.html>`__
-  `build <https://pypa-build.readthedocs.io/en/stable/>`__
-  `twine <https://twine.readthedocs.io/en/latest/#configuration>`__

To help with dependency pinning and build reproduction aiosql leverages `pip-tools <https://github.com/jazzband/pip-tools>`__ to help produce its ``requirements.txt`` and ``dev-requirements.txt`` files.

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

2. Install pip-tools

.. code:: sh

    python -m pip install pip-tools

3. Sync your environment to the dependencies defined in ``dev-requirements.txt``

The requirements file format is compatible with ``pip`` directly. Simply, ``pip install -r dev-requirements.txt``. But, the recommended flow is to use pip-tools to sync your local environment to the exact versions specified.

.. code:: sh

    pip-sync requirments.txt dev-requirements.txt

4. Run tests

.. code:: sh

    pytest

Dependency Management
---------------------

Read much more at `pip-tools <https://github.com/jazzband/pip-tools>`__.

.. code:: sh

    # When you've changed a dependency in setup.cfg/setup.py
    $ pip-compile

    # When you've updated a development dependency.
    $ pip-compile dev-requirements.in

    # Upgrading packages
    $ pip-compile --upgrade-package test-extensions --upgrade-package contextlib2==21.6.0
