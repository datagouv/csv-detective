from frformat import CodeFantoir

PROPORTION = 1

_code_fantoir = CodeFantoir()


def _is(val):
    return isinstance(val, str) and _code_fantoir.is_valid(val)
