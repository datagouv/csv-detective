PROPORTION = 1
jours = {
    'lundi',
    'mardi',
    'mercredi',
    'jeudi',
    'vendredi',
    'samedi',
    'dimanche',
    'lun',
    'mar',
    'mer',
    'jeu',
    'ven',
    'sam',
    'dim'
}


def _is(val):
    '''Renvoie True si les champs peuvent être des jours de la semaine'''
    if not isinstance(val, str):
        return False
    val = val.lower()
    return val in jours
