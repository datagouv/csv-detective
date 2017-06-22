from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude en métropole'''
    val = val.replace(',','.')
    try:
        lat = float(val)
        return lat >= 41.3 and lat <= 51.3 and '.' in val
    except:
        return False
