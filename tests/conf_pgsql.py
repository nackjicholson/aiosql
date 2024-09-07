import pytest
from conf_schema import create_user_blogs, fill_user_blogs, drop_user_blogs
import run_tests as t

# guess psycopg version from a connection
def is_psycopg2(conn):
    return hasattr(conn, "get_dsn_parameters")

try:
    from pytest_postgresql import factories as pg_factories

    @pytest.fixture
    def pg_conn(request):
        """Loads seed data and return a database connection."""
        is_detached = request.config.getoption("postgresql_detached")
        if is_detached:  # pragma: no cover
            # this is *NOT* a connection, it does not have a "cursor"
            pg = request.getfixturevalue("postgresql_noproc")
            import psycopg

            conn = psycopg.connect(
                host=pg.host,
                port=pg.port,
                user=pg.user,
                password=pg.password,
                dbname=pg.dbname,
                options=pg.options,
            )
        else:
            # returns the underlying pytest-postgresql connection
            # which may be psycopg version 2 or 3, depending.
            conn = request.getfixturevalue("postgresql")

        # yield the psycopg? connection
        yield conn

        # done
        conn.close()

    @pytest.fixture
    def pg_params(request, pg_conn):
        """Build postgres connection parameters as a dictionary."""
        if is_psycopg2(pg_conn):  # pragma: no cover
            dsn = pg_conn.get_dsn_parameters()
            del dsn["tty"]
        else:  # assume psycopg 3.x
            dsn = pg_conn.info.get_parameters()
        # non empty password?
        if "password" not in dsn:
            dsn["password"] = request.config.getoption("postgresql_password") or ""
        if "port" not in dsn:
            dsn["port"] = 5432
        return dsn

    @pytest.fixture
    def pg_dsn(request, pg_params):
        """Build a postgres URL connection string."""
        p = pg_params
        yield f"postgres://{p['user']}:{p['password']}@{p['host']}:{p['port']}/{p['dbname']}"

    @pytest.fixture
    def pg_db(rconn, queries):
        create_user_blogs(rconn, queries)
        fill_user_blogs(rconn, queries)
        yield rconn
        drop_user_blogs(rconn, queries)

except ModuleNotFoundError:
    # FIXME empty fixtures to please pytest

    @pytest.fixture
    def pg_conn():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def pg_params():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def pg_dsn():
        raise Exception("unimplemented fixture")

    @pytest.fixture
    def pg_db():
        raise Exception("unimplemented fixture")
