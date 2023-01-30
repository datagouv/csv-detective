import json

PROPORTION = 1


def _is(val):
    '''Detects json'''
    try:
        loaded = json.loads(val)
        if isinstance(loaded, dict) and not(any([geo in loaded for geo in ['coordinates', 'geometry']])):
            return True
    except:
        return False
