from frformat import CodeRNA

PROPORTION = 0.9


def _is(val):
    return isinstance(val, str) and CodeRNA.is_valid(val)
