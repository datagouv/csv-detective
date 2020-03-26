from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude en métropole'''
    try:
        val = float(val.replace(',','.'))
        if int(val) == val:
            return False
        return val >= 41.3 and val <= 51.3
    except:
        return False
