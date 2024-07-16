from frformat import CodePostal, Options

PROPORTION = 0.9

_code_postal = CodePostal(Options())


def _is(val):

    return _code_postal.is_valid(val)
