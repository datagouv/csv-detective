proportion = 1
tags = ["temp"]
python_type = "int"
labels = {
    "year": 1,
    "annee": 1,
    "naissance": 1,
    "exercice": 1,
}


def _is(val):
    try:
        val = int(val)
    except ValueError:
        return False
    return (1800 <= val) and (val <= 2100)


_test_values = {
    True: ["2015"],
    False: ["20166", "123"],
}
