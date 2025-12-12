import re

proportion = 1
tags = ["type"]
python_type = "float"
labels = {"part": 1, "ratio": 1, "taux": 1}

scientific_notation_pattern = r"\d+\.\d+[e|E][+|-]?\d+"


def float_casting(val: str) -> float:
    return float(val.replace(",", "."))


def _is(val):
    """Detects floats (including scientific notation), unless there is an underscore or a plus sign (bad practice)."""
    try:
        if (
            not isinstance(val, str)
            or "_" in val
            or (val.startswith("0") and len(val) > 1 and val[1] not in [".", ","])
        ):
            return False
        elif any([k in val for k in ["+", "e", "E"]]) and not re.match(
            scientific_notation_pattern, val
        ):
            return False
        float_casting(val)
        return True
    except ValueError:
        return False


_test_values = {
    True: ["1", "0", "1764", "-24", "1.2", "1863.23", "-12.7", "0.1", "1.9764E-1", "19.01e-29"],
    False: ["01053", "01053.89", "1e3", "123_456", "123_456.78", "+35", "+35.9"],
}
