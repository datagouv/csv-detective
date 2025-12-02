import re

proportion = 0.8
labels = ["id", "identifiant"]


def _is(val) -> bool:
    return isinstance(val, str) and bool(
        re.match(r"^[{]?[0-9a-fA-F]{8}" + "-?([0-9a-fA-F]{4}-?)" + "{3}[0-9a-fA-F]{12}[}]?$", val)
    )


_test_values = {
    True: ["884762be-51f3-44c3-b811-1e14c5d89262"],
    False: ["0610928327"],
}
