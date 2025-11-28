import re

proportion = 0.8
tags = ["fr"]
labels = [
    "uai",
    "code etablissement",
    "code uai",
    "uai - identifiant",
    "numero uai",
    "rne",
    "numero de l'etablissement",
    "code rne",
    "codeetab",
    "code uai de l'etablissement",
    "ref uai",
    "cd rne",
    "numerouai",
    "numero d etablissement",
    "code etablissement",
    "numero etablissement",
]


def _is(val):
    if not isinstance(val, str) or len(val) != 8:
        return False
    if not bool(re.match(r"^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$", val)):
        return False
    return True


_test_values = {
    True: ["0422170F"],
    False: ["04292E"],
}
