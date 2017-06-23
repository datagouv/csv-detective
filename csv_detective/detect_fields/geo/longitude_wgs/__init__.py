from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une longitude'''
    try:
        val = float(val.replace(',','.'))
        if int(val) == val:
            return False
        return val >= -180 and val <= 180
    except:
        return False
