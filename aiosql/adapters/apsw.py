from .generic import GenericAdapter


class APSWAdapter(GenericAdapter):
    """
    APSW Adapter suitable for `named` parameter style and no with support.
    """

    def select(self, conn, _query_name, sql, parameters, record_class=None):
        cur = self._cursor(conn)
        try:
            cur.execute(sql, parameters)
            if record_class is None:
                results = cur.fetchall()
            else:
                # NOTE must use description on the fly
                results = [
                    record_class(**dict(zip([c[0] for c in cur.description], row))) for row in cur
                ]
        finally:
            cur.close()
        return results
