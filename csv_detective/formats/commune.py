from frformat import Commune, Millesime, Options

proportion = 0.8
tags = ["fr", "geo"]
labels = {
    "commune": 1,
    "ville": 1,
    "libelle commune": 1,
}

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
_commune = Commune(Millesime.LATEST, _options)


def _is(val):
    return isinstance(val, str) and _commune.is_valid(val)


_test_values = {
    True: ["saint denis"],
    False: ["new york", "lion"],
}
