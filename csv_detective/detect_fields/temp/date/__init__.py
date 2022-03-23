from dateutil.parser import parse

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être une date, False sinon'''
    try:
        parse(val, fuzzy=False)
        return True
    except (ValueError, TypeError):
        return False
