proportion = 0.8
tags = ["fr", "temp"]
labels = [
    "jour semaine",
    "type jour",
    "jour de la semaine",
    "saufjour",
    "nomjour",
    "jour",
    "jour de fermeture",
]

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
    val = val.lower()
    return val in jours


_test_values = {
    True: ["lundi"],
    False: ["jour de la biere"],
}
