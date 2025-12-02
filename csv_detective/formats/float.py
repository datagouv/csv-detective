proportion = 1
tags = ["type"]
labels = ["part", "ratio", "taux"]


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


_test_values = {
    True: ["1", "0", "1764", "-24", "1.2", "1863.23", "-12.7", "0.1"],
    False: ["01053", "01053.89", "1e3", "123_456", "123_456.78", "+35", "+35.9"],
}
