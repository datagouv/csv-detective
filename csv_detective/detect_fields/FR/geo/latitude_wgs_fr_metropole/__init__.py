from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une longitude en métropole'''
    try:
        val = float(val.replace(',','.'))
        if int(val) == val:
            return False
        return val >= -5.5 and val <= 9.8
    except:
        return False
