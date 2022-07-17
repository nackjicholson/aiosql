from ..patterns import var_pattern
from .generic import GenericAdapter


def _replacer(match):
    gd = match.groupdict()
    if gd["dblquote"] is not None:
        return gd["dblquote"]
    elif gd["quote"] is not None:
        return gd["quote"]
    else:
        return f'{gd["lead"]}%({gd["var_name"]})s{gd["trail"]}'


class PyFormatAdapter(GenericAdapter):
    """Convert from named to pyformat parameter style"""

    def process_sql(self, _query_name, _op_type, sql):
        return var_pattern.sub(_replacer, sql)
