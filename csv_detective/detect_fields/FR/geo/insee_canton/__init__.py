from frformat import Canton

PROPORTION = 0.9


def _is(val):
    """Match avec le nom des cantons"""
    return isinstance(val, str) and Canton.is_valid(val, strict=False)
