from os.path import dirname, join
from csv_detective.process_text import _process_text
import re
from unidecode import unidecode

PROPORTION = 1

def _is(val):
    '''Renvoie True si les champs peuvent être des mois de l'année'''
    val = unidecode(val.lower())
    mois = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout','septembre','octobre','novembre','decembre','jan','fev','mar','avr','mai','jun','jui','juil','aou','sep','sept','oct','nov','dec']
    return val in mois
