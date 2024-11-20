from frformat import Pays, Options, Millesime

PROPORTION = 0.6

_options = Options(
        ignore_case=True,
        ignore_accents=True,
        replace_non_alphanumeric_with_space=True,
        ignore_extra_whitespace=True
    )
_pays = Pays(Millesime.LATEST, _options)


def _is(val):
    """Match avec le nom des pays"""
    return isinstance(val, str) and _pays.is_valid(val)
