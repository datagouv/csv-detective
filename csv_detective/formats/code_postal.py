from frformat import CodePostal

proportion = 0.9
tags = ["fr", "geo"]
mandatory_label = True
labels = {
    "code postal": 1,
    "postal code": 1,
    "postcode": 1,
    "post code": 1,
    "cp": 0.5,
    "codes postaux": 1,
    "location postcode": 1,
}

_code_postal = CodePostal()


def _is(val):
    return isinstance(val, str) and _code_postal.is_valid(val)


_test_values = {
    True: ["75020", "01000"],
    False: ["77777", "018339"],
}
