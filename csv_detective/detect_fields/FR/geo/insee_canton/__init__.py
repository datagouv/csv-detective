from frformat import Canton, Options, Millesime

PROPORTION = 0.9
_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True
)
_canton = Canton(Millesime.LATEST, _options)


def _is(val):
    """Match avec le nom des cantons"""
    return isinstance(val, str) and _canton.is_valid(val)
