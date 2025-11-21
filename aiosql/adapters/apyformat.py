from .ageneric import AsyncGenericAdapter
from .pyformat import _replacer
from ..utils import VAR_REF


class AsyncPyFormatAdapter(AsyncGenericAdapter):
    """Convert from named to pyformat parameter style."""

    def process_sql(self, query_name, op_type, sql):
        """From named to pyformat."""
        return VAR_REF.sub(_replacer, sql)
