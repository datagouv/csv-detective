from frformat import Departement

PROPORTION = 0.9


def _is(val):
    """Match avec le nom des departements"""
    return isinstance(val, str) and Departement.is_valid(val, strict=False)
