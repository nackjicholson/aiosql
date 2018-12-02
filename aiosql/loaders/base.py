import re
from abc import ABC, abstractmethod
from enum import Enum

from ..exceptions import SQLParseException


class SQLOperationType(Enum):
    SELECT = 0
    INSERT_UPDATE_DELETE = 1
    RETURNING = 2


class QueryLoader(ABC):
    """Abstract Base Class for defining custom aiosql QueryLoader classes.

    Example:
        Defining a custom MyDb loader::

            import anosql


            class MyDbQueryLoader(anosql.QueryLoader):
               def process_sql(self, name, op_type, sql):
                   # ... Provides a hook to make any custom preparations to the sql text.
                   return sql

               def create_fn(self, name, op_type, sql, return_as_dict):
                   # This hook lets you define logic for how to build your query methods.
                   # They take your driver connection and do the work of talking to your database.
                   # The class helps parse your SQL text, and has class level variables such as self.op_type to help you decide
                   # which operation a sql statement intends to perform.
                   def fn(conn, *args, **kwargs):
                       # ...
                       pass

                   return fn


            # To register your query loader as a valid anosql db_type do:
            anosql.register_query_loader("mydb", MyDbQueryLoader())

            # To use make a connection to your db, and pass "mydb" as the db_type:
            import mydbdriver
            conn = mydbriver.connect("...")

            anosql.load_queries("mydb", "path/to/sql/")
            users = anosql.get_users(conn)

            conn.close()

        For concrete examples view the implementation of :py:mod:`aiosql.loaders.psycopg2` and
        :py:mod:`aiosql.loaders.sqlite3` modules.
    """

    op_types = SQLOperationType

    name_pattern = re.compile(r"\w+")
    """
    Pattern: Enforces names are valid python variable names.
    """

    doc_pattern = re.compile(r"\s*--\s*(.*)$")
    """
    Pattern: Identifies SQL comments.
    """

    var_pattern = re.compile(
        r'(?P<dblquote>"[^"]+")|'
        r"(?P<quote>\'[^\']+\')|"
        r"(?P<lead>[^:]):(?P<var_name>[\w-]+)(?P<trail>[^:])"
    )
    """
    Pattern: Identifies variable definitions in SQL code.
    """

    def load(self, query_text):
        """Builds name and function pair from SQL query text to be attached as a dynamic method
        on a :py:class:`aiosql.aiosql.Queries` instance.

        Args:
            query_text (str): SQL Query, comments and name definition.

        Returns:
            tuple(str, callable): Name and function pair.

        """
        lines = query_text.strip().splitlines()
        name = lines[0].replace("-", "_")

        if name.endswith("<!"):
            op_type = SQLOperationType.RETURNING
            name = name[:-2]
        elif name.endswith("!"):
            op_type = SQLOperationType.INSERT_UPDATE_DELETE
            name = name[:-1]
        else:
            op_type = SQLOperationType.SELECT

        return_as_dict = False
        if name.startswith("$"):
            return_as_dict = True
            name = name[1:]

        if not self.name_pattern.match(name):
            raise SQLParseException(f'name must convert to valid python variable, got "{name}".')

        docs = ""
        sql = ""
        for line in lines[1:]:
            match = self.doc_pattern.match(line)
            if match:
                docs += match.group(1) + "\n"
            else:
                sql += line + "\n"

        docs = docs.strip()
        sql = self.process_sql(name, op_type, sql.strip())

        fn = self.create_fn(name, op_type, sql, return_as_dict)
        fn.__name__ = name
        fn.__docs__ = docs

        return name, fn

    @abstractmethod
    def process_sql(self, name, op_type, sql):
        """Abstract method which allows any necessary processing of the SQL content before it can
        be used by your loaded aiosql Queries method.

        For example, the :py:class:`aiosql.loaders.psycopg2.PsycoPG2QueryLoader` class uses this
        function to process ``:variable_name`` style variables into ``%(variable_name)s`` style
        variables for use by the ``psycopg2`` db driver for postgres.

        Args:
            name (str): The name of the sql query.
            op_type (SQLOperationType): The type of SQL operation performed by this query.
            sql (str): The sql as written before processing.

        Returns:

        """
        pass

    @abstractmethod
    def create_fn(self, name, op_type, sql, return_as_dict):
        """Abstract method which builds function to execute sql queries with a database connection.

        The returned function should have the interface ``def fn(conn, *args, **kwargs)``.

        Args:
            name (str): The name of the sql query.
            op_type (SQLOperationType): The type of SQL operation performed by this query.
            sql (str): The processed SQL to be executed.
            return_as_dict (bool): Whether or not to return rows as dictionaries using column names.

        Returns:
            callable: Function to execute SQL and return results.

        """
        pass
