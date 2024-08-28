import pytest
import aiosql

from conf_mysql import my_dsn, my_db, my_conn
from conf_pgsql import pg_conn, pg_params, pg_dsn
from conf_sqlite import sqlite3_db_path
from conf_duckdb import duckdb_db_path, duckdb_conn
from conf_mssql import ms_dsn, ms_db, ms_conn, ms_driver, ms_master


def pytest_addoption(parser):
    # Postgres
    parser.addoption("--postgresql-detached", action="store_true")
    # MySQL and MariaDB
    parser.addoption("--mysql-detached", action="store_true")
    parser.addoption("--mysql-server", default="localhost")
    parser.addoption("--mysql-port", default=3306, type=int)
    parser.addoption("--mysql-user", default="pytest", type=str)
    parser.addoption("--mysql-passwd", default="pytest", type=str)
    parser.addoption("--mysql-dbname", default="pytest", type=str)
    parser.addoption("--mysql-tries", default=1, type=int)
    parser.addoption(
        "--mysql-driver",
        default="MySQLdb",
        choices=["MySQLdb", "mysql.connector", "pymysql", "mariadb"],
        help="which driver to use for creating connections",
    )
    # MS SQL Server
    parser.addoption("--mssql-tries", default=1, type=int)
    parser.addoption("--mssql-driver", default="pymssql")
    parser.addoption("--mssql-user", default="sa")
    parser.addoption("--mssql-password", type=str)
    parser.addoption("--mssql-server", default="localhost")
    parser.addoption("--mssql-port", default=1433, type=int)
    parser.addoption("--mssql-database", default="master")


# test adapter registering and overriding
aiosql.aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)
aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)
