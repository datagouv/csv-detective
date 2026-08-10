from csv_detective.formats.float import _is as is_float

proportion = 0.8
description = "Percentage"
labels = {"pourcent": 1, "part": 0.75, "pct": 0.75}


def _is(val) -> bool:
    if not isinstance(val, str) or not val or val[-1] != "%":
        return False
    return is_float(val[:-1])


_test_values = {
    True: ["120%", "-20.2%"],
    False: ["200", "100 pourcents"],
}
