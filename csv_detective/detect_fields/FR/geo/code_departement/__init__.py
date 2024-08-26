from frformat import NumeroDepartement

PROPORTION = 1


def _is(val):
    return NumeroDepartement.is_valid(val, strict=False)
