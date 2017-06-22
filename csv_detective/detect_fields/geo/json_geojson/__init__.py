from csv_detective.process_text import _process_text
import json

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
    except:
        pass

    return False
