from frformat import CodeCommuneInsee, Millesime

PROPORTION = 0.75

_code_commune_insee = CodeCommuneInsee(Millesime.LATEST)


def _is(val):
    return _code_commune_insee.is_valid(val)
