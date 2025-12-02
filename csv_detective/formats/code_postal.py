from frformat import CodePostal

proportion = 0.9
tags = ["fr", "geo"]
labels = [
    "code postal",
    "postal code",
    "postcode",
    "post code",
    "cp",
    "codes postaux",
    "location postcode",
]

_code_postal = CodePostal()


def _is(val):
    return isinstance(val, str) and _code_postal.is_valid(val)


_test_values = {
    True: ["75020", "01000"],
    False: ["77777", "018339"],
}
