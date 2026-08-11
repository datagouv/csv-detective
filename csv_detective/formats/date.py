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
# the unanchored bodies are reused to build the datetime patterns
_jjmmaaaa = r"(0[1-9]|[12][0-9]|3[01])SEP(0[1-9]|1[0-2])SEP((19|20)\d{2})".replace("SEP", seps)
_mmjjaaaa = r"(0[1-9]|1[0-2])SEP(0[1-9]|[12][0-9]|3[01])SEP((19|20)\d{2})".replace("SEP", seps)
_aaaammjj = r"((19|20)\d{2})SEP(0[1-9]|1[0-2])SEP(0[1-9]|[12][0-9]|3[01])".replace(
    "SEP", seps + "?"
)
# matches JJ-MM-AAAA with any of the listed separators
jjmmaaaa_pattern = f"^{_jjmmaaaa}$"
# matches MM-JJ-AAAA (US order) with any of the listed separators
mmjjaaaa_pattern = f"^{_mmjjaaaa}$"
# matches AAAA-MM-JJ with any of the listed separators OR NO SEPARATOR
aaaammjj_pattern = f"^{_aaaammjj}$"
# the date part of a datetime, in any of the three orders
date_part_pattern = f"(?:{_aaaammjj}|{_jjmmaaaa}|{_mmjjaaaa})"
# matches JJ-mmm-AAAA and JJ-mmm...mm-AAAA with any of the listed separators OR NO SEPARATOR
string_month_pattern = (
    r"^(0[1-9]|[12][0-9]|3[01])SEP(jan|fev|feb|mar|avr|apr"
    r"|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec|janvier|fevrier|mars|avril|"
    r"mai|juin|juillet|aout|septembre|octobre|novembre|decembre)SEP"
    r"([0-9]{2}$|(19|20)[0-9]{2}$)"
).replace("SEP", seps + "?")


def _is(val, meta=None) -> bool:
    # many early stops, to cut processing time
    # and avoid the costly use of date_casting as much as possible
    # /!\ timestamps are considered ints, not dates
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return False
    # if it's a usual date pattern
    candidates = date_format_candidates(val)
    if candidates:
        narrow_column_formats(meta, candidates)
        return True
    # a date whose format can't be pinned down (mixed separators) is still a date
    if (
        re.match(aaaammjj_pattern, val)
        or re.match(jjmmaaaa_pattern, val)
        or re.match(mmjjaaaa_pattern, val)
        or re.match(string_month_pattern, val, re.IGNORECASE)
    ):
        return True
    if re.match(r"^-?\d+[\.|,]\d+$", val):
        # regular floats are excluded
        return False
    # not enough digits => not a date (slightly arbitrary)
    if sum(char.isdigit() for char in val) / len(val) < threshold:
        return False
    # last resort
    res = date_casting(val)
    if not res or res.hour or res.minute or res.second:
        return False
    return True


def date_format_candidates(val: str) -> set[str]:
    """Returns every strptime format the value could be read with.

    A value whose two first components are both <= 12 ("07/03/2024") reads equally well as
    day-first or month-first: it yields both formats, and only the column settles which one
    applies (see narrow_column_formats and resolve_date_format).
    """
    if not isinstance(val, str) or len(val) > 20 or len(val) < 8:
        return set()

    if re.match(aaaammjj_pattern, val):
        if len(val) == 8:
            return {"%Y%m%d"}
        sep = val[4]
        return {f"%Y{sep}%m{sep}%d"} if val[7] == sep else set()

    day_first = bool(re.match(jjmmaaaa_pattern, val))
    month_first = bool(re.match(mmjjaaaa_pattern, val))
    if not (day_first or month_first):
        return set()
    sep = val[2]
    if val[5] != sep:
        return set()
    candidates = set()
    if day_first:
        candidates.add(f"%d{sep}%m{sep}%Y")
    if month_first:
        candidates.add(f"%m{sep}%d{sep}%Y")
    return candidates


def datetime_format_candidates(val: str, has_tz: bool) -> set[str]:
    """Returns every strptime format the datetime value could be read with.

    Only meaningful for values that already matched a datetime pattern.
    """
    # the date part is 10 characters long with separators, 8 without (AAAAMMJJ)
    for date_len in (10, 8):
        date_candidates = date_format_candidates(val[:date_len])
        if date_candidates:
            break
    else:
        return set()
    time_part = val[date_len:]
    # time_part starts with the date/time separator, "T" or a blank
    suffix = f"{time_part[0]}%H:%M:%S"
    if "." in time_part:
        suffix += ".%f"
    if has_tz:
        suffix += "%z"
    return {fmt + suffix for fmt in date_candidates}


def narrow_column_formats(meta: dict | None, candidates: set[str]) -> None:
    """Keeps in meta only the formats that fit every value seen so far in the column.

    Taken one by one, values are often ambiguous; a column rarely is. A single "25/03/2024"
    rules out the month-first reading for all the other values of its column.
    """
    if meta is None or not candidates:
        return
    known = meta.get("date_format")
    meta["date_format"] = candidates if known is None else known & candidates


def resolve_date_format(candidates: set[str]) -> list[str] | None:
    """Picks a column's format among the ones that fit all of its values."""
    if len(candidates) == 1:
        return list(candidates)
    # Several formats fit every value: nothing in the column tells day-first from month-first.
    # Day-first is the overwhelming majority of what csv-detective is fed, so it wins the tie.
    day_first = sorted(fmt for fmt in candidates if fmt.startswith("%d"))
    return day_first[:1] or None


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
