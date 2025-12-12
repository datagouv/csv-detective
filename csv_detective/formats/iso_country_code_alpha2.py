import re
from os.path import dirname, join

proportion = 1
tags = ["geo"]
labels = {
    "iso country code": 1,
    "code pays": 1,
    "pays": 1,
    "country": 1,
    "nation": 1,
    "pays code": 1,
    "code pays (iso)": 1,
    "code": 0.5,
}

with open(join(dirname(__file__), "data", "iso_country_code_alpha2.txt"), "r") as iofile:
    liste_pays = set(iofile.read().split("\n"))


def _is(val):
    if not isinstance(val, str) or not bool(re.match(r"[a-zA-Z]{2}$", val)):
        return False
    return val.upper() in liste_pays


_test_values = {
    True: ["FR", "sj"],
    False: ["XX", "A", "FRA"],
}
