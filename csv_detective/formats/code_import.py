import re

proportion = 0.9
tags = ["fr"]
labels = ["code"]

regex = r"^(\d{3}[SP]\d{4,10}(.\w{1,3}\d{0,5})?|\d[A-Z0-9]\d[SP]\w(\w-?\w{0,2}\d{0,6})?)$"


def _is(val):
    return isinstance(val, str) and bool(re.match(regex, val))


_test_values = {
    True: ["123S1871092288"],
    False: ["AA751PEE00188854", "W123456789"],
}
