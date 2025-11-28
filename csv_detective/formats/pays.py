from frformat import Millesime, Options, Pays

proportion = 0.6
tags = ["fr", "geo"]
labels = [
    "pays",
    "payslieu",
    "paysorg",
    "country",
    "pays lib",
    "lieupays",
    "pays beneficiaire",
    "nom du pays",
    "journey start country",
    "libelle pays",
    "journey end country",
]

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
_pays = Pays(Millesime.LATEST, _options)


def _is(val):
    return isinstance(val, str) and _pays.is_valid(val)


_test_values = {
    True: ["france", "italie"],
    False: ["amerique", "paris"],
}
