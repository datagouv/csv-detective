from frformat import CodeRegion, Millesime

proportion = 1
tags = ["fr", "geo"]
labels = [
    "code region",
    "reg",
    "code insee region",
    "region",
]

_code_region = CodeRegion(Millesime.LATEST)


def _is(val):
    return isinstance(val, str) and _code_region.is_valid(val)


_test_values = {
    True: ["32"],
    False: ["55"],
}
