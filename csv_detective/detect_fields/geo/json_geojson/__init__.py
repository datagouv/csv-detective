import json
from json import JSONDecodeError

PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre geojson'''

    try:
        j = json.loads(val)
        if 'type' in j and 'coordinates' in j:
            return True
        if 'geometry' in j:
            if 'coordinates' in j['geometry']:
                return True
    except JSONDecodeError:
        pass
    except TypeError:
        pass

    return False
