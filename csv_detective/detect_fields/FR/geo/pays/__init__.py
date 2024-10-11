from frformat import Pays

PROPORTION = 0.6


def _is(val):
    """Match avec le nom des pays"""
    return isinstance(val, str) and Pays.is_valid(val, strict=False)
