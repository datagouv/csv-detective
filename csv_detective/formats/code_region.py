from frformat import CodeRegion, Millesime

proportion = 1
tags = ["fr", "geo"]
mandatory_label = True
labels = {
    "code region": 1,
    "reg": 0.5,
    "code insee region": 1,
    "region": 1,
}

_code_region = CodeRegion(Millesime.LATEST)


def _is(val):
    return isinstance(val, str) and _code_region.is_valid(val)


_test_values = {
    True: ["32"],
    False: ["55"],
}
