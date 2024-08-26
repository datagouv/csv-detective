from frformat import Region

PROPORTION = 1


def _is(val):
    """Match avec le nom des regions"""
    return Region.is_valid(val, strict=False)
