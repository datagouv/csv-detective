from ..float import _is as is_float

currencies = set(["€", "$", "£", "¥"])

PROPORTION = 0.8


def _is(val: str):
    if not isinstance(val, str) or val[-1] not in currencies:
        return False
    return is_float(val[:-1])
