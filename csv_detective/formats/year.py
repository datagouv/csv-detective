proportion = 1
description = "Year"
tags = ["temp"]
python_type = "int"
labels = {
    "year": 1,
    "annee": 1,
    "naissance": 1,
    "exercice": 1,
}


def _is(val: str | int) -> bool:
    if not isinstance(val, int):
        try:
            val = int(val)
        except ValueError:
            return False
    return (1800 <= val) and (val <= 2100)


_test_values = {
    True: ["2015", 2020],
    False: ["20166", "123", "2020.5", 156],
}
