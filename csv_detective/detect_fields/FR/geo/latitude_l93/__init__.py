from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude en Lambert 93'''
    val = val.replace(',','.')
    try:
        lat = float(val)
        return lat >= 6037008 and lat <= 7230728 and '.' in val
    except:
        return False
