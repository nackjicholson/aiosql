import pytest
import aiosql

from conf_mysql import my_dsn, my_db, my_conn
from conf_pgsql import pg_conn, pg_params, pg_dsn
from conf_sqlite import sqlite3_db_path


def pytest_addoption(parser):
    parser.addoption("--postgresql-detached", action="store_true")
    parser.addoption("--mysql-detached", default=False, action="store_true")
    parser.addoption(
        "--mysql-driver",
        default="MySQLdb",
        choices=["MySQLdb", "mysql.connector", "pymysql", "mariadb"],
        help="which driver to use for creating connections",
    )


# test adapter registering and overriding
aiosql.aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)
aiosql.register_adapter("named", aiosql.adapters.GenericAdapter)
