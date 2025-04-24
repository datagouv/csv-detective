from ..float import _is as is_float

PROPORTION = 0.8


def _is(val: str):
    if not isinstance(val, str) or val[-1] != "%":
        return False
    return is_float(val[:-1])
