from .generic import GenericAdapter


class Pg8000Adapter(GenericAdapter):
    def _cursor(self, conn):
        import pg8000

        return pg8000.Cursor(conn, paramstyle="named")
