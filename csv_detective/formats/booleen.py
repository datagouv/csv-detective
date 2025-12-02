proportion = 1
tags = ["type"]
labels = ["is ", "has ", "est "]

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


def _is(val):
    return isinstance(val, str) and val.lower() in liste_bool


_test_values = {
    True: ["oui", "0", "1", "yes", "false", "True"],
    False: ["nein", "ja", "2", "-0"],
}
