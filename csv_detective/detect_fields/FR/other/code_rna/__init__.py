from frformat import CodeRNA, Options

PROPORTION = 0.9

_code_rna = CodeRNA(Options())


def _is(val):

    return _code_rna.is_valid(val)
