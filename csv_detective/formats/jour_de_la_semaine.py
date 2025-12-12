proportion = 0.8
tags = ["fr", "temp"]
labels = {
    "jour semaine": 1,
    "type jour": 1,
    "jour de la semaine": 1,
    "saufjour": 1,
    "nomjour": 1,
    "jour": 0.75,
    "jour de fermeture": 1,
}

jours = {
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
    "lun",
    "mar",
    "mer",
    "jeu",
    "ven",
    "sam",
    "dim",
}


def _is(val):
    if not isinstance(val, str):
        return False
    return val.lower() in jours


_test_values = {
    True: ["lundi"],
    False: ["jour"],
}
