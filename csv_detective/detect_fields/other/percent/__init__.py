from ..float import _is as is_float


def _is(val: str):
    if not isinstance(val, str) or val[-1] != "%":
        return False
    return is_float(val[:-1])
