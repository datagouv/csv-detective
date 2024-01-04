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


def _is(val):
    '''Renvoie True si val peut être une date, False sinon
    On ne garde que les regex pour les cas où parse() ne convient pas'''

    # matches 02/12 03 and 02_12 2003
    a = bool(
        re.match(
            r'^(0[1-9]|[12][0-9]|3[01])[ -/_](0[1-9]|1[012])[ -/_]'
            r'([0-9]{2}|(19|20)[0-9]{2}$)',
            val
        )
    )

    # matches 02052003
    b = bool(
        re.match(
            r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])([0-9]{2}|'
            r'(19|20){2}$)',
            val
        )
    )

    # matches JJ*MM*AAAA
    c = bool(
        re.match(
            r'^(0[1-9]|[12][0-9]|3[01]).?(0[1-9]|1[012]).?(19|20)?\d\d$', val))

    # matches JJ-mmm-AAAA and matches JJ-mmm...mm-AAAA
    d = bool(
        re.match(
            r'^(0[1-9]|[12][0-9]|3[01])[ -/_;.:,](jan|fev|feb|mar|avr|apr'
            r'|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec|janvier|fevrier|mars|avril|'
            r'mai|juin|jullet|aout|septembre|octobre|novembre|decembre)[ -/_;.:,]'
            r'([0-9]{2}$|(19|20)[0-9]{2}$)',
            unidecode(val)
        )
    )

    return (is_dateutil_date(val) and not is_float(val)) or a or b or c or d
