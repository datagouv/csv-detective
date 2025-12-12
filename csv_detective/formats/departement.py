from frformat import Departement, Millesime, Options

proportion = 0.9
tags = ["fr", "geo"]
labels = {
    "departement": 1,
    "libelle du departement": 1,
    "deplib": 1,
    "nom dept": 1,
    "dept": 0.75,
    "libdepartement": 1,
    "nom departement": 1,
    "libelle dep": 1,
    "libelle departement": 1,
    "lb departements": 1,
    "dep libusage": 1,
    "lb departement": 1,
    "nom dep": 1,
}

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
