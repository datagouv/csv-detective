from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une longitude'''
    val = val.replace(',','.')
    try:
        lon = float(val)
        return lon >= -180 and lon <= 180 and '.' in val
    except:
        return False
