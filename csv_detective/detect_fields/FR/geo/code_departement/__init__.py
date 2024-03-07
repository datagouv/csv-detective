from frformat import NumeroDepartement

PROPORTION = 1


def _is(val):
    """Renvoie True si val peut être un code_département, False sinon"""
    alternative_corsica = {"2a", "2b"}
    return NumeroDepartement.is_valid(val) or val in alternative_corsica
