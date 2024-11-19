from frformat import CodePostal

PROPORTION = 0.9

_code_postal = CodePostal()


def _is(val):

    return _code_postal.is_valid(val)
