PROPORTION = 1
bool_mapping = {
    "1": True,
    "0": False,
    "vrai": True,
    "faux": False,
    "true": True,
    "false": False,
    "oui": True,
    "non": False,
    "yes": True,
    "no": False,
    "y": True,
    "n": False,
    "o": True,
}

liste_bool = set(bool_mapping.keys())


def bool_casting(val: str) -> bool:
    return bool_mapping.get(val.lower())


def _is(val: str) -> bool:
    '''Détecte les booléens'''
    return isinstance(val, str) and val.lower() in liste_bool
