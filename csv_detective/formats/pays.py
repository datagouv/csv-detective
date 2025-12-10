from frformat import Millesime, Options, Pays

proportion = 0.6
tags = ["fr", "geo"]
labels = {
    "pays": 1,
    "payslieu": 1,
    "paysorg": 1,
    "country": 1,
    "pays lib": 1,
    "lieupays": 1,
    "pays beneficiaire": 1,
    "nom du pays": 1,
    "libelle pays": 1,
}

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
