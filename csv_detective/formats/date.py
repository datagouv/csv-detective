import re
from datetime import datetime

from dateparser import parse as date_parser
from dateutil.parser import ParserError
from dateutil.parser import parse as dateutil_parser

proportion = 1
tags = ["temp", "type"]
SHARED_DATE_LABELS = [
    "date",
    "mise à jour",
    "modifie",
    "maj",
    "datemaj",
    "update",
    "created",
    "modified",
]
labels = SHARED_DATE_LABELS + [
    "jour",
    "periode",
    "dpc",
    "yyyymmdd",
    "aaaammjj",
]


def date_casting(val: str) -> datetime | None:
    """For performance reasons, we try first with dateutil and fallback on dateparser"""
    try:
        return dateutil_parser(val)
    except ParserError:
        return date_parser(val)
    except Exception:
        return None


threshold = 0.3
seps = r"[\s/\-\*_\|;.,]"
# matches JJ-MM-AAAA with any of the listed separators
jjmmaaaa_pattern = r"^(0[1-9]|[12][0-9]|3[01])SEP(0[1-9]|1[0-2])SEP((19|20)\d{2})$".replace(
    "SEP", seps
)
# matches AAAA-MM-JJ with any of the listed separators OR NO SEPARATOR
aaaammjj_pattern = r"^((19|20)\d{2})SEP(0[1-9]|1[0-2])SEP(0[1-9]|[12][0-9]|3[01])$".replace(
    "SEP", seps + "?"
)
# matches JJ-mmm-AAAA and JJ-mmm...mm-AAAA with any of the listed separators OR NO SEPARATOR
string_month_pattern = (
    r"^(0[1-9]|[12][0-9]|3[01])SEP(jan|fev|feb|mar|avr|apr"
    r"|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec|janvier|fevrier|mars|avril|"
    r"mai|juin|jullet|aout|septembre|octobre|novembre|decembre)SEP"
    r"([0-9]{2}$|(19|20)[0-9]{2}$)"
).replace("SEP", seps + "?")


def _is(val):
    # early stops, to cut processing time
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return False
    # if it's a usual date pattern
    if any(
        # with this syntax, if any of the first value is True, the next ones are not computed
        [
            bool(re.match(jjmmaaaa_pattern, val))
            or bool(re.match(aaaammjj_pattern, val))
            or bool(re.match(string_month_pattern, val, re.IGNORECASE))
        ]
    ):
        return True
    if sum([char.isdigit() for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    if not res or res.hour or res.minute or res.second:
        return False
    return True


_test_values = {
    True: [
        "1960-08-07",
        "12/02/2007",
        "15 jan 1985",
        "15 décembre 1985",
        "02 05 2003",
        "20030502",
        "1993-12/02",
    ],
    False: [
        "1993-1993-1993",
        "39-10-1993",
        "19-15-1993",
        "15 tambour 1985",
        "12152003",
        "20031512",
        "02052003",
    ],
}
