import re
from os.path import dirname, join

from csv_detective.formats.iso_country_code_alpha2 import labels  # noqa

proportion = 1
tags = ["geo"]

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
