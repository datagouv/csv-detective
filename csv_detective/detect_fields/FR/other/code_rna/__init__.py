from frformat import CodeRNA

PROPORTION = 0.9

_code_rna = CodeRNA()


def _is(val):
    return isinstance(val, str) and _code_rna.is_valid(val)
