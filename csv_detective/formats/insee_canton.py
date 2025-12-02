from frformat import Canton, Millesime, Options

proportion = 0.9
tags = ["fr", "geo"]
labels = [
    "insee canton",
    "canton",
    "cant",
    "nom canton",
]

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
_canton = Canton(Millesime.LATEST, _options)


def _is(val):
    return isinstance(val, str) and _canton.is_valid(val)


_test_values = {
    True: ["nantua"],
    False: ["california"],
}
