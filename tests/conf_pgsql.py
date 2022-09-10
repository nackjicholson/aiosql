import pytest
from conf_schema import USERS_DATA_PATH, BLOGS_DATA_PATH, create_user_blogs

# guess psycopg version
def is_psycopg2(conn):
    return hasattr(conn, "get_dsn_parameters")


try:
    from pytest_postgresql import factories as pg_factories

    @pytest.fixture
    def pg_conn(request):
        """Loads seed data before returning db connection."""
        if request.config.getoption("postgresql_detached"):  # pragma: no cover
            conn = request.getfixturevalue("postgresql_noproc")
        else:
            conn = request.getfixturevalue("postgresql")

        # Loads data from blogdb fixture data
        with conn.cursor() as cur:

            for tc in create_user_blogs("pgsql"):
                cur.execute(tc)

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

        yield conn

    @pytest.fixture()
    def pg_params(pg_conn):
        if is_psycopg2(pg_conn):  # pragma: no cover
            dsn = pg_conn.get_dsn_parameters()
            del dsn["tty"]
        else:  # assume psycopg 3.x
            dsn = pg_conn.info.get_parameters()
        return dsn

    @pytest.fixture()
    def pg_dsn(request, pg_params):
        p = pg_params
        pw = request.config.getoption("postgresql_password")
        yield f"postgres://{p['user']}:{pw}@{p['host']}:{p['port']}/{p['dbname']}"

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
