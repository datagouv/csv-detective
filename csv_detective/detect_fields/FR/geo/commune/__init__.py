from frformat import Commune, Options, Millesime

PROPORTION = 0.9

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True
)
_commune = Commune(Millesime.LATEST, _options)


def _is(val):
    """Match avec le nom des communes"""
    return isinstance(val, str) and _commune.is_valid(val)
