import re

proportion = 0.8
labels = ["id", "objectid"]


def _is(val):
    return isinstance(val, str) and bool(re.match(r"^[0-9a-fA-F]{24}$", val))


_test_values = {
    True: ["62320e50f981bc2b57bcc044"],
    False: ["884762be-51f3-44c3-b811-1e14c5d89262", "0230240284a66e"],
}
