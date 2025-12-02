from frformat import Millesime, NumeroDepartement, Options

proportion = 1
tags = ["fr", "geo"]
labels = [
    "code departement",
    "code_departement",
    "dep",
    "departement",
    "dept",
]

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
_numero_departement = NumeroDepartement(Millesime.LATEST, _options)


def _is(val):
    return isinstance(val, str) and _numero_departement.is_valid(val)


_test_values = {
    True: ["75", "2A", "2b", "974", "01"],
    False: ["00", "96", "101"],
}
