import pytest
from conf_schema import USERS_DATA_PATH, BLOGS_DATA_PATH, create_user_blogs, drop_user_blogs
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

        # TODO use the tested driver instead?
        queries = t.queries("psycopg2" if is_psycopg2(conn) else "psycopg")

        # loads data from blogdb fixture data
        create_user_blogs(conn, queries)

        # TODO improve data loading
        with conn.cursor() as cur:
            # guess whether we have a psycopg 2 or 3 connection
            with USERS_DATA_PATH.open() as fp:
                if is_psycopg2(conn):  # pragma: no cover
                    cur.copy_from(
                        fp, "users", sep=",", columns=["username", "firstname", "lastname"]
                    )
                else:
                    with cur.copy(
                        "COPY users(username, firstname, lastname) FROM STDIN (FORMAT CSV)"
                    ) as cope:
                        cope.write(fp.read())

            with BLOGS_DATA_PATH.open() as fp:
                if is_psycopg2(conn):  # pragma: no cover
                    cur.copy_from(
                        fp, "blogs", sep=",", columns=["userid", "title", "content", "published"]
                    )
                else:  # assume psycopg 3
                    with cur.copy(
                        "COPY blogs(userid, title, content, published) FROM STDIN (FORMAT CSV)"
                    ) as cope:
                        cope.write(fp.read())

        conn.commit()

        # yield the psycopg? connection
        yield conn

        # cleanup
        drop_user_blogs(conn, queries)

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

except ModuleNotFoundError:
    # FIXME empty fixtures to please pytest

    @pytest.fixture
    def pg_conn():
        raise Exception("undefined fixture")

    @pytest.fixture
    def pg_params():
        raise Exception("undefined fixture")

    @pytest.fixture
    def pg_dsn():
        raise Exception("undefined fixture")
