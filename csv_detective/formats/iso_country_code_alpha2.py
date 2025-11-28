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

with open(join(dirname(__file__), "data", "iso_country_code_alpha2.txt"), "r") as iofile:
    liste_pays = iofile.read().split("\n")
liste_pays = set(liste_pays)


def _is(val):
    if not isinstance(val, str) or not bool(re.match(r"[A-Z]{2}$", val)):
        return False
    return val in liste_pays


_test_values = {
    True: ["FR"],
    False: ["XX", "A", "FRA"],
}
