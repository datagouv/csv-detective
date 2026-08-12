import re
import unicodedata
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Iterable

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


# Formats that strptime cannot express are prefixed with this marker and read by parse() itself.
# So far only text months: strptime only knows the ones of the process locale.
CUSTOM_PREFIX = "csvd:"

SEPARATORS = " /-*_|;.,"
MIN_LENGTH = 8  # "1/2/2024"
MAX_LENGTH = 20
MIN_YEAR = 1900
MAX_YEAR = 2099

# Standard forms come from the system locale tables (the CLDR data that PHP and Java also use),
# tolerated variants are what published files actually contain. Adding a language is one entry.
MONTH_NAMES: dict[str, list[list[str]]] = {
    "fr": [
        ["janvier", "janv", "jan"],
        ["fevrier", "fevr", "fev"],
        ["mars", "mar"],
        ["avril", "avr"],
        ["mai"],
        ["juin"],
        ["juillet", "juil"],
        ["aout", "aou"],
        ["septembre", "sept", "sep"],
        ["octobre", "oct"],
        ["novembre", "nov"],
        ["decembre", "dec"],
    ],
    "en": [
        ["january", "jan"],
        ["february", "feb"],
        ["march", "mar"],
        ["april", "apr"],
        ["may"],
        ["june", "jun"],
        ["july", "jul"],
        ["august", "aug"],
        ["september", "sept", "sep"],
        ["october", "oct"],
        ["november", "nov"],
        ["december", "dec"],
    ],
}


def _build_month_index() -> dict[str, int]:
    index: dict[str, int] = {}
    ambiguous: set[str] = set()
    for months in MONTH_NAMES.values():
        for number, names in enumerate(months, start=1):
            for name in names:
                if index.setdefault(name, number) != number:
                    # the same spelling means two different months depending on the language,
                    # reading it would be a guess (this is what rules out "jui" for fr)
                    ambiguous.add(name)
    for name in ambiguous:
        del index[name]
    return index


MONTHS = _build_month_index()

_DIRECTIVES = {
    "%d": r"(?P<day>\d{1,2})",
    "%b": r"(?P<month>[^\W\d_]+)\.?",
    "%Y": r"(?P<year>\d{4})",
    "%y": r"(?P<short_year>\d{2})",
}
_TOKENS = re.compile(r"%.|.", re.DOTALL)


@lru_cache(maxsize=None)
def _compiled(fmt: str) -> re.Pattern:
    return re.compile(
        "".join(_DIRECTIVES.get(token, re.escape(token)) for token in _TOKENS.findall(fmt))
    )


def _deaccent(val: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", val.lower())
        if not unicodedata.combining(char)
    )


def _parse_custom(val: str, fmt: str) -> datetime | None:
    match = _compiled(fmt).fullmatch(val)
    if match is None:
        return None
    month = MONTHS.get(_deaccent(match["month"]))
    if month is None:
        return None
    groups = match.groupdict()
    if groups.get("year"):
        year = int(groups["year"])
    else:
        # same two-digit window as strptime's %y
        short_year = int(groups["short_year"])
        year = 2000 + short_year if short_year < 69 else 1900 + short_year
    try:
        return datetime(year, month, int(groups["day"]))
    except ValueError:
        return None


def parse(val: str, fmt: str) -> datetime | None:
    """Reads a value with one of our formats, the custom ones included."""
    if fmt.startswith(CUSTOM_PREFIX):
        parsed = _parse_custom(val, fmt[len(CUSTOM_PREFIX) :])
    else:
        try:
            parsed = datetime.strptime(val, fmt)
        except (ValueError, TypeError):
            return None
    if parsed is None or not (MIN_YEAR <= parsed.year <= MAX_YEAR):
        return None
    return parsed


# the order is the preference: an ambiguous value is read day-first, as French files are the
# overwhelming majority of what csv-detective is fed
_TEMPLATES = (
    "%d{sep}%m{sep}%Y",
    "%m{sep}%d{sep}%Y",
    "%Y{sep}%m{sep}%d",
)
_TEXT_MONTH_TEMPLATES = (
    CUSTOM_PREFIX + "%d{sep}%b{sep}%Y",
    CUSTOM_PREFIX + "%d{sep}%b{sep}%y",
)


def separator_of(val: str) -> str | None:
    """The single separator the value uses, "" if it uses none, None if it mixes several."""
    found = {
        char
        for index, char in enumerate(val)
        if char in SEPARATORS
        # the full stop of an abbreviated month is not a separator ("15 janv. 1985")
        and not (char == "." and index and val[index - 1].isalpha())
    }
    if len(found) > 1:
        return None
    return found.pop() if found else ""


def date_templates(val: str, *, text_month: bool = True) -> list[str]:
    """Every format the value could plausibly be read with, most preferred first."""
    sep = separator_of(val)
    if sep is None:
        return []
    if not sep:
        # without a separator, only the year-first order is unambiguous enough to be trusted
        return ["%Y%m%d"]
    templates = _TEMPLATES + (_TEXT_MONTH_TEMPLATES if text_month else ())
    return [template.format(sep=sep) for template in templates]


_DATETIME_SPLIT = re.compile(r"(?P<date>.+?)(?P<t>[T ])(?P<time>\d{1,2}:\d{2}.*)")
_TIME_SUFFIXES = ("%H:%M:%S", "%H:%M:%S.%f", "%H:%M")


def datetime_templates(val: str, *, aware: bool) -> list[str]:
    """Every format the datetime value could plausibly be read with, most preferred first."""
    match = _DATETIME_SPLIT.fullmatch(val)
    if match is None:
        return []
    date_part = match["date"]
    if not (MIN_LENGTH <= len(date_part) <= MAX_LENGTH):
        return []
    timezone = "%z" if aware else ""
    return [
        f"{date}{match['t']}{time}{timezone}"
        for date in date_templates(date_part, text_month=False)
        for time in _TIME_SUFFIXES
    ]


def infer_column_format(
    values: Iterable[Any],
    templates_for: Callable[[str], list[str]],
) -> str | None:
    """The single format that reads every value of the column, None if no format reads them all.

    Taken one by one, values are often ambiguous ("07/03/2024" reads both ways); a column rarely
    is, as one "25/03/2024" rules out the month-first reading for all the others. A column no
    format fits is not a date at all, which is why this both detects and describes.
    """
    candidates: list[str] | None = None
    for val in values:
        if not isinstance(val, str):
            return None
        if candidates is None:
            candidates = templates_for(val)
        candidates = [fmt for fmt in candidates if parse(val, fmt) is not None]
        if not candidates:
            return None
    return candidates[0] if candidates else None


def _templates_for(val: str) -> list[str]:
    if not (MIN_LENGTH <= len(val) <= MAX_LENGTH):
        return []
    return date_templates(val)


def _infer(values: Iterable[Any]) -> str | None:
    return infer_column_format(values, _templates_for)


def _is(val: Any) -> bool:
    return _infer([val]) is not None


_test_values = {
    True: [
        "1960-08-07",
        "12/02/2007",
        "15 jan 1985",
        "15 décembre 1985",
        "02 05 2003",
        "20030502",
        "2003.05.02",
        "1/2/2024",
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
        "1993-12/02",
        "15 jui 1985",
    ],
}
