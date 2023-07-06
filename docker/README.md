# AioSQL Docker Tests

As MySQL et MariaDB cannot be installed one alongside the other easily,
this directory provides a docker solution with 3 servers (for postgres,
mysql and mariadb) and their clients. Tests with databases sqlite3 and duckdb
are run with mariadb because it has the lowest load.

## Servers

They rely on the official images for `postgres`, `mysql` and `mariadb`.

## Clients

They are built on top of `ubuntu` because using the official `python`
image could not be made to work for all 5 databases.
See docker specifications in `dockerfile.python-*`.

## Makefile

Run docker compose for `pytest` or `coverage`.

```shell
# get/update docker images
docker image pull postgres
docker image pull mariadb
docker image pull mysql
docker image pull ubuntu
# generate client images
make docker.aiosql
# run tests in ..
make docker.pytest
make docker.coverage
```

## Miscellaneous Commands

```sh
docker run -it --add-host=host.docker.internal:host-gateway python bash
docker build -t aiosql-python-mysql -f dockerfile.python-mysql .
```
