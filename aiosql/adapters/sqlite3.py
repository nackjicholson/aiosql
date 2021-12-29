from .generic import GenericAdapter

class SQLite3Adapter(GenericAdapter):
    # overwrites some methods using sqlite3-specific non-standard methods

    @staticmethod
    def insert_update_delete(conn, _query_name, sql, parameters):
        conn.execute(sql, parameters)

    @staticmethod
    def insert_update_delete_many(conn, _query_name, sql, parameters):
        conn.executemany(sql, parameters)

    @staticmethod
    def insert_returning(conn, _query_name, sql, parameters):
        cur = conn.cursor()
        try:
            cur.execute(sql, parameters)
            results = cur.lastrowid
        finally:
            cur.close()
        return results

    @staticmethod
    def execute_script(conn, sql):
        conn.executescript(sql)
        return "DONE"
