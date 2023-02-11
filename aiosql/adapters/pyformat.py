from .generic import GenericAdapter
from ..utils import VAR_REF


def _replacer(match):
    gd = match.groupdict()
    if gd["dquote"] is not None:
        return gd["dquote"]
    elif gd["squote"] is not None:
        return gd["squote"]
    else:
        return f'{gd["lead"]}%({gd["var_name"]})s'


class PyFormatAdapter(GenericAdapter):
    """Convert from named to pyformat parameter style"""

    def process_sql(self, _query_name, _op_type, sql):
        return VAR_REF.sub(_replacer, sql)
