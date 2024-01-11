
PROPORTION = 1
liste_des_dep = {str(x).zfill(2) for x in range(1, 20)} | \
                {'2A', '2B', '984', '986', '987', '988', '989', '2a', '2b'} |  \
                {str(x) for x in range(21, 96)} | \
                {str(x) for x in range(971, 979)}


def _is(val):
    '''Renvoie True si val peut être un code_département, False sinon'''
    return val in liste_des_dep
