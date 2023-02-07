import re

PROPORTION = 1


def _is(val):
    '''Renvoie True si val peut être une date au format rfc822, False sinon
    AAAA-MM-JJ HH-MM-SS avec indication du fuseau horaire

    '''

    val = val.lower()
    a = bool(
        re.match(
            r'^((mon|tue|wed|thu|fri|sat|sun),|)( )?\d{1,2} '
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) '
            r'\d\d(\d\d|) \d\d\:\d\d(\:\d\d|) '
            r'(ut|gmt|est|edt|cst|cdt|mst|mdt|pst|pdt|([+-]\d{4}))$',
            val,
            re.IGNORECASE
        )
    )

    return a
