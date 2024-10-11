import re

PROPORTION = 1


def _is(val):
    '''Repere les codes UAI de l'éducation nationale'''

    # test sur la longueur
    if not isinstance(val, str) or len(val) != 8:
        return False

    if not bool(re.match(r'^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$', val)):
        return False
    return True
