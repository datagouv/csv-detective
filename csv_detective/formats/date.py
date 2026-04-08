import re
from datetime import datetime

from dateparser import parse as date_parser
from dateutil.parser import ParserError
from dateutil.parser import parse as dateutil_parser

proportion = 1
description = "Date (flexible formats)"
tags = ["temp", "type"]
python_type = "date"
SHARED_DATE_LABELS = {
    "date": 1,
    "mise à jour": 1,
    "modifie": 1,
    "maj": 0.75,
    "datemaj": 1,
    "update": 1,
    "created": 1,
    "modified": 1,
}
labels = SHARED_DATE_LABELS | {
    "jour": 0.75,
    "periode": 0.75,
    "dpc": 0.5,
    "yyyymmdd": 1,
    "aaaammjj": 1,
}


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
    r"mai|juin|juillet|aout|septembre|octobre|novembre|decembre)SEP"
    r"([0-9]{2}$|(19|20)[0-9]{2}$)"
).replace("SEP", seps + "?")


def _is(val) -> bool:
    # many early stops, to cut processing time
    # and avoid the costly use of date_casting as much as possible
    # /!\ timestamps are considered ints, not dates
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return False
    # if it's a usual date pattern
    if (
        # with this syntax, if any of the first value is True, the next ones are not computed
        bool(re.match(jjmmaaaa_pattern, val))
        or bool(re.match(aaaammjj_pattern, val))
        or bool(re.match(string_month_pattern, val, re.IGNORECASE))
    ):
        return True
    if re.match(r"^-?\d+[\.|,]\d+$", val):
        # regular floats are excluded
        return False
    # not enough digits => not a date (slightly arbitrary)
    if sum([char.isdigit() for char in val]) / len(val) < threshold:
        return False
    # last resort
    res = date_casting(val)
    if not res or res.hour or res.minute or res.second:
        return False
    return True


def detect_strptime_format(val: str) -> str | None:
    """Returns the strptime format string for a date value, or None if format can't be determined."""
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return None

    if re.match(jjmmaaaa_pattern, val):
        sep = val[2]
        if val[5] != sep:
            return None
        return f"%d{sep}%m{sep}%Y"

    if re.match(aaaammjj_pattern, val):
        if len(val) == 8:
            return "%Y%m%d"
        sep = val[4]
        if val[7] != sep:
            return None
        return f"%Y{sep}%m{sep}%d"

    return None


def detect_strptime_format_datetime(val: str) -> str | None:
    """Returns the strptime format string for a datetime value, or None if format can't be determined."""
    from csv_detective.formats.datetime_aware import pat as aware_pat
    from csv_detective.formats.datetime_naive import pat as naive_pat

    if not isinstance(val, str) or len(val) < 15:
        return None

    for pat, has_tz in [(naive_pat, False), (aware_pat, True)]:
        if not re.match(pat, val):
            continue
        sep = val[4]
        if sep.isdigit():
            sep = ""
        elif val[7] != sep:
            return None

        date_end = 8 if not sep else 10
        tsep = val[date_end]

        time_part = val[date_end + 1:]
        has_microseconds = "." in time_part

        fmt = f"%Y{sep}%m{sep}%d{tsep}%H:%M:%S"
        if has_microseconds:
            fmt += ".%f"
        if has_tz:
            fmt += "%z"
        return fmt

    return None


_test_values = {
    True: [
        "1960-08-07",
        "12/02/2007",
        "15 jan 1985",
        "15 décembre 1985",
        "02 05 2003",
        "20030502",
        "2003.05.02",
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
        "6.27367393749392839",
    ],
}
