import re

proportion = 0.9
tags = ["fr"]
labels = [
    "siren",
    "siren organisme designe",
    "siren organisme designant",
    "n° siren",
    "siren organisme",
    "siren titulaire",
    "numero siren",
    "epci",
]


def _is(val):
    """Repere les codes SIREN"""
    if not isinstance(val, str):
        return False
    val = val.replace(" ", "")
    if not bool(re.match(r"^[0-9]{9}$", val)):
        return False
    # Vérification par clé propre aux codes siren
    cle = 0
    pair = False
    for x in val:
        y = int(x) * (1 + pair)
        cle += y // 10 + y % 10
        pair = not pair
    return cle % 10 == 0


_test_values = {
    True: ["552 100 554", "552100554"],
    False: ["42"],
}
