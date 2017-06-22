from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude'''
    val = val.replace(',','.')
    try:
        lat = float(val)
        return lat >= -90 and lat <= 90 and '.' in val
    except:
        return False
