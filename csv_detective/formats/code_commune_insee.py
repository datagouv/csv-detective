from frformat import CodeCommuneInsee, Millesime

proportion = 0.75
tags = ["fr", "geo"]
labels = [
    "code commune insee",
    "code insee",
    "codes insee",
    "code commune",
    "code insee commune",
    "insee",
    "code com",
    "com",
]

_code_commune_insee = CodeCommuneInsee(Millesime.LATEST)


def _is(val):
    return isinstance(val, str) and _code_commune_insee.is_valid(val)


_test_values = {
    True: ["91471", "01053"],
    False: ["914712", "01000"],
}
