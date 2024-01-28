from .generic import GenericAdapter
from ..utils import VAR_REF


def _replacer(match):
    """Regex hook for named to pyformat conversion."""
    gd = match.groupdict()
    if gd["dquote"] is not None:  # "..."
        return gd["dquote"]
    elif gd["squote"] is not None:  # '...'
        return gd["squote"]
    else:  # :something to %(something)s
        return f'{gd["lead"]}%({gd["var_name"]})s'


class PyFormatAdapter(GenericAdapter):
    """Convert from named to pyformat parameter style."""

    def process_sql(self, _query_name, _op_type, sql):
        """From named to pyformat."""
        return VAR_REF.sub(_replacer, sql)
