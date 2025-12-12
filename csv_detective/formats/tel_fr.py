import re

proportion = 0.7
tags = ["fr"]
labels = {
    "telephone": 1,
    "tel": 1,
    "phone": 1,
    "num tel": 1,
    "tel mob": 1,
}


def _is(val):
    if not isinstance(val, str):
        return False

    if len(val) < 10:
        return False

    val = val.replace(".", "").replace("-", "").replace(" ", "")

    match_1 = bool(re.match(r"^(0|\+33|0033)?[0-9]{9}$", val))
    return match_1


_test_values = {
    True: ["0134643467"],
    False: ["6625388263", "01288398"],
}
