from os.path import dirname, join

from csv_detective.parsing.text import _process_text

proportion = 0.8
tags = ["fr"]
labels = [
    "code ape",
    "code activite (ape)",
    "code naf",
    "code naf organisme designe",
    "code naf organisme designant",
    "base sirene : code ape de l'etablissement siege",
]

f = open(join(dirname(__file__), "data", "insee_ape700.txt"), "r")
condes_insee_ape = f.read().split("\n")
# removing empty str due to additionnal line in file
del condes_insee_ape[-1]
condes_insee_ape = set(condes_insee_ape)
f.close()


def _is(val):
    if not isinstance(val, str):
        return False
    val = _process_text(val).upper()
    return val in condes_insee_ape


_test_values = {True: ["0116Z"], False: ["0116A"]}
