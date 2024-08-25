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

## MS SQL Server

The online documentation is quite poor.

```sh
docker pull mcr.microsoft.com/mssql/server:2022-latest
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Abc123.." -e "MSSQL_PID=Developer" \
  -p 1433:1433  --name mssqltest --hostname mssqltest -d mcr.microsoft.com/mssql/server:2022-latest
docker exec -it mssqltest /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "Abc123.."
# type a command
# go
```
