import re
from os.path import dirname, join

from csv_detective.formats.iso_country_code_alpha2 import labels  # noqa

proportion = 1
tags = ["geo"]

with open(join(dirname(__file__), "data", "iso_country_code_alpha3.txt"), "r") as iofile:
    liste_pays = set(iofile.read().split("\n"))


def _is(val):
    """Renvoie True si val peut etre un code iso pays alpha-3, False sinon"""
    if not isinstance(val, str) or not bool(re.match(r"[a-zA-Z]{3}$", val)):
        return False
    return val.upper() in liste_pays


_test_values = {
    True: ["FRA", "brb"],
    False: ["XXX", "FR", "A"],
}
