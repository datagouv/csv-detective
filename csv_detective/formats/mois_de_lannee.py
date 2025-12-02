from unidecode import unidecode

proportion = 1
tags = ["fr", "temp"]
labels = ["mois", "month"]

mois = {
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
    "jan",
    "fev",
    "mar",
    "avr",
    "mai",
    "jun",
    "jui",
    "juil",
    "aou",
    "sep",
    "sept",
    "oct",
    "nov",
    "dec",
}


def _is(val):
    """Renvoie True si les champs peuvent être des mois de l'année"""
    if not isinstance(val, str):
        return False
    val = unidecode(val.lower())
    return val in mois


_test_values = {
    True: ["JUIN", "décembre"],
    False: ["november"],
}
