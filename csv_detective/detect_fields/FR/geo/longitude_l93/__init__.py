from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une longitude en métropole'''
    val = val.replace(',','.')
    try:
        lon = float(val)
        return lon >= -357823 and lon <= 1313633 and '.' in val
    except:
        return False
