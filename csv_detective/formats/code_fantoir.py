from frformat import CodeFantoir

proportion = 1
tags = ["fr", "geo"]
labels = [
    "cadastre1",
    "code fantoir",
    "fantoir",
]

_code_fantoir = CodeFantoir()


def _is(val):
    return isinstance(val, str) and _code_fantoir.is_valid(val)


_test_values = {
    True: ["7755A", "B150B", "ZA04C", "ZB03D"],
    False: ["7755", "ZA99A"],
}
