from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être un code_département, False sinon'''
    liste_des_dep = [str(x).zfill(2) for x in range(1,20)] + \
                    ['2A', '2B', '971','972','973','974','976', '2a', '2b'] +  \
                    [str(x) for x in range(21,96)]
    # TODO: Enregistrer la liste des départements dans un fichier texte séparé
    return val in liste_des_dep

#from os.path import dirname, join
#from csv_detective.process_text import _process_text
import re

#PROPORTION = 0.9

#def _is(val):
 #   '''Match avec le code des departements'''
  #  f = open(join(dirname(__file__), 'code_ departement.txt'), 'r')
  #  liste = f.read().split('\n')
   # f.close()
    #val = _process_text(val)
    # return val in liste
