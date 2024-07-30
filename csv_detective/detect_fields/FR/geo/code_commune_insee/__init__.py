from frformat import CodeCommuneInsee

PROPORTION = 0.75

_code_commune_insee = CodeCommuneInsee()


def _is(val):
    return _code_commune_insee.is_valid(val)
