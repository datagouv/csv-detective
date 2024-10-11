from frformat import NumeroDepartement

PROPORTION = 1


def _is(val):
    return isinstance(val, str) and NumeroDepartement.is_valid(val, strict=False)
