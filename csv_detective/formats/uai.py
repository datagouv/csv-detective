import re

proportion = 0.8
tags = ["fr"]
labels = {
    "uai": 1,
    "code etablissement": 1,
    "code uai": 1,
    "uai - identifiant": 1,
    "numero uai": 1,
    "rne": 0.75,
    "numero de l'etablissement": 1,
    "code rne": 1,
    "codeetab": 1,
    "code uai de l'etablissement": 1,
    "ref uai": 1,
    "cd rne": 1,
    "numerouai": 1,
    "numero d etablissement": 1,
    "numero etablissement": 1,
}


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
