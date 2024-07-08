from frformat import NumeroDepartement, Options

PROPORTION = 1


def _is(val):
    options = Options(
        ignore_case=True,
        ignore_non_alphanumeric=True,
        ignore_extra_white_space=True,
        ignore_accents=True
        )
    return NumeroDepartement.is_valid(val, options)
