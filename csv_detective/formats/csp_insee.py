from os.path import dirname, join

from csv_detective.parsing.text import _process_text

proportion = 1
tags = ["fr"]
labels = [
    "csp insee",
    "csp",
    "categorie socioprofessionnelle",
]

f = open(join(dirname(__file__), "data", "csp_insee.txt"), "r")
codes_insee = f.read().split("\n")
# removing empty str due to additionnal line in file
del codes_insee[-1]
codes_insee = set(codes_insee)
f.close()


def _is(val):
    if not isinstance(val, str):
        return False
    val = _process_text(val)
    return val in codes_insee


_test_values = {
    True: ["employes de la poste"],
    False: ["super-heros"],
}
