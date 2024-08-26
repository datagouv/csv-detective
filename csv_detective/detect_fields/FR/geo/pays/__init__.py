from frformat import Pays

PROPORTION = 0.6


def _is(val):
    """Match avec le nom des pays"""
    return Pays.is_valid(val, strict=False)
