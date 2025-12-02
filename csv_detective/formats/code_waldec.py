import re

proportion = 0.9
tags = ["fr"]
labels = ["code waldec", "waldec"]

regex = r"^W\d[\dA-Z]\d{7}$"


def _is(val):
    return isinstance(val, str) and bool(re.match(regex, val))


_test_values = {
    True: ["W123456789", "W2D1234567"],
    False: ["AA751PEE00188854"],
}
