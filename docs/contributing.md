# Contributing

First, thank you for considering to make a contribution to this project. Spending your valuable time helping make this project better is deeply appreciated. All kinds of contributions are helpful and welcome.

- Report issues https://github.com/nackjicholson/aiosql/issues
- Review or make your own pull requests https://github.com/nackjicholson/aiosql/pulls
- Write documentation https://github.com/nackjicholson/aiosql/tree/master/docs

Whether you have an idea for a feature improvement or have found a troubling bug, thank you for being here.

## Packaging & Distribution

This aiosql repository uses the python standard packaging tools. Read about them in more detail at the following links.

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPA - Packaging & Distributing projects*](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [setuptools](https://setuptools.readthedocs.io/en/latest/index.html)
- [build](https://pypa-build.readthedocs.io/en/stable/)
- [twine](https://twine.readthedocs.io/en/latest/#configuration)

To help with dependency pinning and build reproduction aiosql leverages [pip-tools](https://github.com/jazzband/pip-tools) to help produce its `requirements.txt` and `dev-requirements.txt` files.

## Development Setup

1. Create a virtual environment

```sh
git clone git@github.com:nackjicholson/aiosql.git
cd aiosql
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

All subsequent steps will assume you are using python within your activated virtual environment.

2. Install pip-tools

```sh
python -m pip install pip-tools
```

3. Sync your environment to the dependencies defined in `dev-requirements.txt`

The requirements file format is compatible with `pip` directly. Simply, `pip install -r dev-requirements.txt`. But, the recommended flow is to use pip-tools to sync your local environment to the exact versions specified.

```sh
pip-sync requirments.txt dev-requirements.txt
```

## Dependency Management

Read much more at [pip-tools](https://github.com/jazzband/pip-tools).

```sh
# When you've changed a dependency in setup.cfg/setup.py
$ pip-compile --generate-hashes

# When you've updated a development dependency.
$ pip-compile --generate-hashes dev-requirements.in

# Upgrading packages
$ pip-compile --upgrade-package django --upgrade-package requests==2.0.0
```
