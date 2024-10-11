import re
from dateutil.parser import parse, ParserError
from csv_detective.detect_fields.other.float import _is as is_float
from unidecode import unidecode

PROPORTION = 1
# /!\ this is only for dates, not datetimes which are handled by other utils


def is_dateutil_date(val: str) -> bool:
    # we don't want to get datetimes here, so length restriction
    # longest date string expected here is DD-septembre-YYYY, so 17 characters
    if len(val) > 17:
        return False
    try:
        res = parse(val, fuzzy=False)
        if res.hour or res.minute or res.second:
            return False
        return True
    except (ParserError, ValueError, TypeError, OverflowError):
        return False


seps = r'[\s/\-\*_\|;.,]'
# matches JJ-MM-AAAA with any of the listed separators
pat = r'^(0[1-9]|[12][0-9]|3[01])SEP(0[1-9]|1[0-2])SEP((19|20)\d{2})$'.replace('SEP', seps)
# matches AAAA-MM-JJ with any of the listed separators OR NO SEPARATOR
tap = r'^((19|20)\d{2})SEP(0[1-9]|1[0-2])SEP(0[1-9]|[12][0-9]|3[01])$'.replace('SEP', seps + '?')
# matches JJ-mmm-AAAA and JJ-mmm...mm-AAAA with any of the listed separators OR NO SEPARATOR
letters = (
    r'^(0[1-9]|[12][0-9]|3[01])SEP(jan|fev|feb|mar|avr|apr'
    r'|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec|janvier|fevrier|mars|avril|'
    r'mai|juin|jullet|aout|septembre|octobre|novembre|decembre)SEP'
    r'(\d{2}|\d{4})$'
).replace('SEP', seps + '?')


def _is(val):
    '''Renvoie True si val peut être une date, False sinon
    On ne garde que les regex pour les cas où parse() ne convient pas'''
    return isinstance(val, str) and (
        (is_dateutil_date(val) and not is_float(val))
        or bool(re.match(letters, unidecode(val)))
        or bool(re.match(pat, val))
        or bool(re.match(tap, val))
    )
