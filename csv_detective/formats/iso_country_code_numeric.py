import re
from os.path import dirname, join

proportion = 1
tags = ["geo"]
labels = [
    "iso country code",
    "code pays",
    "pays",
    "country",
    "nation",
    "pays code",
    "code pays (iso)",
]

with open(join(dirname(__file__), "data", "iso_country_code_numeric.txt"), "r") as iofile:
    liste_pays = iofile.read().split("\n")
liste_pays = set(liste_pays)


def _is(val):
    """Renvoie True si val peut etre un code iso pays numerique, False sinon"""
    if not isinstance(val, str) or not bool(re.match(r"[0-9]{3}$", val)):
        return False
    return val in liste_pays


_test_values = {
    True: ["250"],
    False: ["003"],
}
