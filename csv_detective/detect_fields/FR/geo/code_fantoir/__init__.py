from frformat import CodeFantoir

PROPORTION = 1


def _is(val):
    return isinstance(val, str) and CodeFantoir.is_valid(val)
