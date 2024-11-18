from frformat import Commune

PROPORTION = 0.9


def _is(val):
    """Match avec le nom des communes"""
    return isinstance(val, str) and Commune.is_valid(val, strict=False)
