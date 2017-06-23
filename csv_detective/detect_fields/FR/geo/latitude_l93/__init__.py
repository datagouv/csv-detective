from csv_detective.process_text import _process_text

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude en Lambert 93'''
    try:
        val = float(val.replace(',','.'))
        if int(val) == val:
            return False
        return val >= 6037008 and val <= 7230728
    except:
        return False
