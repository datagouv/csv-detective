from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être une date, False sinon'''
    # matches 1993-12/02
    a = bool(re.match(r'^(19|20)\d\d[ -/_;.:,](0[1-9]|1[012])[ -/_;.:,](0[1-9]|[12][0-9]|3[01])$', val))
#ok
    # matches 02/12 03 and 02_12 2003
    b = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_;.:,](0[1-9]|1[012])[ -/_;.:,]([0-9]{2}$|(19|20)[0-9]{2}$)', val))
#ok
    # matches 02052003
    c = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])([0-9]{2}$|(19|20){2}$)', val))
#ok mais precision bof
    # matches 19931202
    d = bool(re.match(r'^(19|20)\d\d(0[1-9]|1[012])(0[1-9]$|[12][0-9]$|3[01]$)', val))
#ok mais precision bof
    # matches JJ-MM-AAAA
    e = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01]).?(0[1-9]|1[012]).?(19|20)?\d\d$', val))
# à supprimer car précision trop faible exemple 22z11z1991
    # matches JJ-mmm-AAAA
    f = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_;.:,](jan|fev|feb|mar|avr|apr|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec)[ -/_;.:,]([0-9]{2}$|(19|20)[0-9]{2}$)', val))

    return a or b or c or d or e or f
