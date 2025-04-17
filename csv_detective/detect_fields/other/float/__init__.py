PROPORTION = 1


def float_casting(val: str) -> float:
    return float(val.replace(",", "."))


def _is(val):
    """Detects floats, assuming that tables will not have scientific
    notations (3e6) or "+" in the string. "-" is still accepted."""
    try:
        if (
            not isinstance(val, str)
            or any([k in val for k in ["_", "+", "e", "E"]])
            or (val.startswith("0") and len(val) > 1 and val[1] not in [".", ","])
        ):
            return False
        float_casting(val)
        return True
    except ValueError:
        return False
