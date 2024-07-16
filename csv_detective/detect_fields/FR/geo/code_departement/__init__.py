from frformat import NumeroDepartement, Options

PROPORTION = 1

_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True
)
_numero_departement = NumeroDepartement(_options)


def _is(val):

    return _numero_departement.is_valid(val)
