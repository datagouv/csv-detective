import re

proportion = 0.9
description = "French association identifier, from the [WALDEC registry](https://www.data.gouv.fr/datasets/repertoire-national-des-associations)"
tags = ["fr"]
labels = {"code waldec": 1, "waldec": 1}

regex = r"^W\d[\dA-Z]\d{7}$"


def _is(val) -> bool:
    return isinstance(val, str) and bool(re.match(regex, val))


_test_values = {
    True: ["W123456789", "W2D1234567"],
    False: ["AA751PEE00188854"],
}
