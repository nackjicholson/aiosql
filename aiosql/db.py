#
# This marvelous code is Public Domain.
#

from typing import Any, Dict, Set, List, Union, Callable
import logging as log
import functools as ft
import aiosql as sql  # type: ignore


class DB:
    """Hides database connection and queries in here.

    The class provides the DB-API 2.0 connection methods,
    and SQL execution methods from `aiosql`.

    ```Python
    import aiosql
    db = aiosql.DB('sqlite', 'blogs.db', 'blogs.sql')
    db.publish_blogs(userid=1, title='hello', content='world', published='2020-08-17')
    …
    db.close()
    db.connect()
    db.publish_blogs(userid=2, title='hi', content='bonjour', published='2038-01-19')
    db.close
    ```
    """

    def __init__(
        self,
        db: str,
        conn: Union[str, Callable],
        queries: Union[str, None] = None,
        options: Union[None, str, Dict[str, Any]] = None,
        auto_reconnect: bool = True,
        debug: bool = False,
        **conn_options,
    ):
        """DB constructor

        - db: database engine, `sqlite` or `postgres`
        - conn: database-specific connection string, or connection generator function
        - queries: file holding queries for `aiosql`, or None
        - options: database-specific options in various forms
        - auto_reconnect: whether to reconnect on connection errors
        - debug: debug mode generate more logs through `logging`
        - conn_options: database-specific `kwargs` constructor options
        """
        log.info(f"creating DB for {db}")
        # database connection
        SQLITE = ("sqlite3", "sqlite")
        POSTGRES = ("pg", "postgres", "postgresql", "psycopg2")
        if db in SQLITE:
            self._db = "sqlite3"
        elif db in POSTGRES:
            self._db = "psycopg2"
        else:  # keep it as is, trusting that some adapter is available
            self._db = db
        # accept connection options as they are
        self._conn_options: Dict[str, Any] = {}
        if options is None:
            pass
        elif isinstance(options, str):
            import ast

            self._conn_options.update(ast.literal_eval(options))
        elif isinstance(options, dict):
            self._conn_options.update(options)
        else:
            raise Exception(f"unexpected type for options: {type(options)}")
        self._conn_options.update(conn_options)
        # connection function
        if isinstance(conn, str):
            if self._db == "sqlite3":
                import sqlite3 as dbd

                def cf(self):
                    return dbd.connect(conn, **self._conn_options)

            elif self._db == "psycopg2":
                import psycopg2 as dbd  # type: ignore

                def cf(self):
                    return dbd.connect(conn, **self._conn_options)

            else:
                raise Exception(f"cannot create connection for db {self._db}")
        elif callable(conn):

            def cf(self):
                return conn(**self._conn_options)

        else:
            raise Exception(f"cannot create connection for {conn}")
        # overwrite predefined _connect
        setattr(DB, "_connect", cf)
        # queries
        self._queries_file = queries
        self._debug = debug
        self._auto_reconnect = auto_reconnect
        self._conn = None
        self._reconn = True
        self._count: Dict[str, int] = {}
        self._queries: List[sql.aiosql.Queries] = []
        self._available_queries: Set[str] = set()
        if queries is not None:
            self.add_queries_from_path(queries)

    def _call_fn(self, query, fn, *args, **kwargs):
        """Forward method call to aiosql query

        On connection failure, it will try to reconnect on the next call
        if auto_reconnect was specified.

        This may or may not be a good idea, but it should be: the failure
        raises an exception which should abort the current request, so that
        the next call should be on a different request.
        """
        if self._debug:
            log.debug(f"DB y: {query}({args}, {kwargs})")
        if self._reconn and self._auto_reconnect:
            self._reconnect()
        try:
            self._count[query] += 1
            return fn(self._conn, *args, **kwargs)
        except Exception as error:
            log.info(f"DB {self._db} query {query} failed: {error}")
            # coldly rollback on any error
            try:
                self._conn.rollback()
            except Exception as rolerr:
                log.warning(f"DB {self._db} rollback failed: {rolerr}")
            # detect a connection error for psycopg2, to attempt a reconnection
            # should more cases be handled?
            if hasattr(self._conn, "closed") and self._conn.closed == 2 and self._auto_reconnect:
                self._reconn = True
            raise error

    def _create_fns(self, queries: sql.aiosql.Queries):
        """Create call forwarding to insert the database connection."""
        self._queries.append(queries)
        for q in queries.available_queries:
            f = getattr(queries, q)
            if callable(f):
                setattr(self, q, ft.partial(self._call_fn, q, getattr(queries, q)))
                self._available_queries.add(q)
                self._count[q] = 0

    def add_queries_from_path(self, fn: str):
        """Load queries from a file or directory."""
        self._create_fns(sql.from_path(fn, self._db))

    def add_queries_from_str(self, qs: str):
        """Load queries from a string."""
        self._create_fns(sql.from_str(qs, self._db))

    def _connect(self):
        """Create an actual connection."""
        raise Exception(f"method to be replaced dynamically")

    def _reconnect(self):
        """Try to reconnect to database."""
        log.info(f"DB {self._db}: reconnecting")
        if self._conn is not None:
            # attempt at closing but ignore errors
            try:
                self._conn.close()
            except Exception as error:
                log.error(f"DB {self._db} close: {error}")
        self._conn = self._connect()
        self._reconn = False

    def connect(self):
        """Create database connection, if needed.

        It can be closed with `close`.
        """
        if self._conn is None:
            self._conn = self._connect()

    def cursor(self):
        """Get a cursor on the current connection.

        This allow to do some raw SQL.
        """
        self.connect()
        return self._conn.cursor()

    def commit(self):
        """Commit current database transaction."""
        self._conn.commit()

    def rollback(self):
        """Rollback current database transaction."""
        self._conn.rollback()

    def close(self):
        """Close underlying database connection.

        The database connection can be re-created with `connect`.
        """
        self._conn.close()
        self._conn = None

    def __str__(self):
        return f"connection to {self._db} database"

    def __del__(self):
        if self._conn is not None:
            self.close()
