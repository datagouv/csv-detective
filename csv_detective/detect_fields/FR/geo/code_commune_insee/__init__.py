from frformat import CodeCommuneInsee, Options

PROPORTION = 0.75

_code_commune_insee = CodeCommuneInsee(Options())


def _is(val):
    return _code_commune_insee.is_valid(val)
