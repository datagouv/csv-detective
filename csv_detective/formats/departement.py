from frformat import Departement, Millesime, Options

proportion = 0.9
tags = ["fr", "geo"]
labels = [
    "departement",
    "libelle du departement",
    "deplib",
    "nom dept",
    "dept",
    "libdepartement",
    "nom departement",
    "libelle dep",
    "libelle departement",
    "lb departements",
    "dep libusage",
    "lb departement",
    "nom dep",
]

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
_departement = Departement(Millesime.LATEST, _options)


def _is(val):
    return isinstance(val, str) and _departement.is_valid(val)


_test_values = {
    True: ["essonne"],
    False: ["alabama", "auvergne"],
}
