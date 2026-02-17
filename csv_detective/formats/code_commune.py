from frformat import CodeCommuneInsee, Millesime

proportion = 0.75
tags = ["fr", "geo"]
mandatory_label = True
labels = {
    "code commune insee": 1,
    "code insee": 1,
    "codes insee": 1,
    "code commune": 1,
    "code insee commune": 1,
    "insee": 0.75,
    "code com": 1,
    "com": 0.5,
    "code": 0.5,
}

_code_commune_insee = CodeCommuneInsee(Millesime.LATEST)


def _is(val):
    return isinstance(val, str) and _code_commune_insee.is_valid(val)


_test_values = {
    True: ["91471", "01053"],
    False: ["914712", "01000"],
}
