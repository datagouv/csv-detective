import re
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Callable, Iterable

from dateparser import parse as date_parser
from dateutil.parser import ParserError
from dateutil.parser import parse as dateutil_parser
from unidecode import unidecode

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

# The only shape made of nothing but digits, and hence the only one a year window has to guard:
# eight bare digits are just a number, of which about one in thirty reads as a valid YYYYMMDD.
# A value that carries separators is specific enough on its own, so no year bounds it — museum
# records and civil registers are routinely dated well before 1900.
_NO_SEPARATOR_DATE = "%Y%m%d"
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


def build_month_index(month_names: dict[str, list[list[str]]]) -> dict[str, int]:
    index: dict[str, int] = {}
    ambiguous: set[str] = set()
    for months in month_names.values():
        for number, names in enumerate(months, start=1):
            for name in names:
                if index.setdefault(name, number) != number:
                    # a spelling that means two different months depending on the language cannot
                    # be read; no current entry does, this guards the languages added later
                    ambiguous.add(name)
    for name in ambiguous:
        del index[name]
    return index


MONTHS = build_month_index(MONTH_NAMES)

_DIRECTIVES = {
    # the ordinal suffix is part of how English writes a day ("31st december 2022")
    "%d": r"(?P<day>\d{1,2})(?:st|nd|rd|th)?",
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


def _parse_custom(val: str, fmt: str) -> datetime | None:
    match = _compiled(fmt).fullmatch(val)
    if match is None:
        return None
    month = MONTHS.get(unidecode(match["month"]).lower())
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


_OPTIONAL_PART = re.compile(r"\[([^\]]*)\]")


@lru_cache(maxsize=None)
def _variants(fmt: str) -> tuple[str, ...]:
    """Expands the optional parts of a format, the most complete one first.

    A column whose source only prints fractional seconds when they are non-zero uses one format
    with an optional part, not two competing ones.
    """
    match = _OPTIONAL_PART.search(fmt)
    if match is None:
        return (fmt,)
    head, tail = fmt[: match.start()], fmt[match.end() :]
    return _variants(head + match.group(1) + tail) + _variants(head + tail)


_UTC_NAME = re.compile(r"\b(?:GMT|UTC)$", re.IGNORECASE)


def _without_prefix(fmt: str) -> str:
    return fmt[len(CUSTOM_PREFIX) :] if fmt.startswith(CUSTOM_PREFIX) else fmt


def _read(val: str, fmt: str) -> datetime | None:
    fmt = _without_prefix(fmt)
    if "%b" in fmt:
        return _parse_custom(val, fmt)
    if "%Z" in fmt and not _UTC_NAME.search(val):
        # %Z also accepts whatever the machine's own zone is called, which we would have no
        # offset for; GMT and UTC are the two names we can turn into a timezone ourselves
        return None
    try:
        parsed = datetime.strptime(val, fmt)
    except (ValueError, TypeError):
        return None
    if "%Z" in fmt:
        # strptime reads the name but drops it, leaving a naive datetime
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse(val: str, fmt: str) -> datetime | None:
    """Reads a value with one of our formats, the custom ones included."""
    for variant in _variants(fmt):
        parsed = _read(val, variant)
        if parsed is None:
            continue
        if _without_prefix(variant).startswith(_NO_SEPARATOR_DATE) and not (
            MIN_YEAR <= parsed.year <= MAX_YEAR
        ):
            continue
        return parsed
    return None


# the order is the preference: an ambiguous value is read day-first, as French files are the
# overwhelming majority of what csv-detective is fed
_DAY_OR_MONTH_FIRST = (
    "%d{sep}%m{sep}%Y",
    "%m{sep}%d{sep}%Y",
)
_DAY_OR_MONTH_FIRST_SHORT = (
    "%d{sep}%m{sep}%y",
    "%m{sep}%d{sep}%y",
)
# ISO first, but the year can also be followed by the day ("2022-31-12")
_YEAR_FIRST = (
    "%Y{sep}%m{sep}%d",
    "%Y{sep}%d{sep}%m",
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


def _marked(template: str) -> str:
    """Marks the formats strptime cannot read as-is, so that consumers can tell them apart."""
    if "[" in template and not template.startswith(CUSTOM_PREFIX):
        return CUSTOM_PREFIX + template
    return template


# every template starts with a digit, so a value that does not cannot be read by any of them.
# Ruling those out with one match is what keeps the hot path off strptime, which costs an order
# of magnitude more than a regex.
_STARTS_LIKE_DATE = re.compile(r"\d")
_HAS_LETTER = re.compile(r"[^\W\d_]")


@lru_cache(maxsize=None)
def _numeric_templates(sep: str, year_first: bool, short_year: bool) -> tuple[str, ...]:
    if not sep:
        # without a separator, only the year-first order is unambiguous enough to be trusted
        return (_NO_SEPARATOR_DATE,)
    if year_first:
        templates = _YEAR_FIRST
    elif short_year:
        templates = _DAY_OR_MONTH_FIRST_SHORT
    else:
        templates = _DAY_OR_MONTH_FIRST
    return tuple(template.format(sep=sep) for template in templates)


@lru_cache(maxsize=None)
def _text_month_templates(sep: str) -> tuple[str, ...]:
    return tuple(template.format(sep=sep) for template in _TEXT_MONTH_TEMPLATES)


def date_templates(val: str, *, text_month: bool = True) -> tuple[str, ...]:
    """Every format the value could plausibly be read with, most preferred first.

    Only the shapes that can possibly read the value are returned: one with a letter can only
    have a text month, and %Y wants four digits where %d wants one or two, so the position of
    the first separator settles the order. A two-digit last component is %y, not %Y.
    Trying the others would be as many failed strptime.
    """
    if not _STARTS_LIKE_DATE.match(val):
        return ()
    sep = separator_of(val)
    if sep is None:
        return ()
    if _HAS_LETTER.search(val):
        return _text_month_templates(sep) if text_month and sep else ()
    year_first = bool(sep) and val.index(sep) == 4
    short_year = bool(sep) and not year_first and len(val) - val.rindex(sep) - 1 == 2
    return _numeric_templates(sep, year_first, short_year)


_DATETIME_SPLIT = re.compile(r"(?P<date>.+?)(?P<t>[T ])(?P<time>\d{1,2}:\d{2}.*)")
# the fraction is listed on its own before the optional form, so that a column that always prints
# it (or never does) is described exactly, and only a column that mixes both falls back on "[.%f]"
_TIME_SUFFIXES = ("%H:%M:%S", "%H:%M:%S.%f", "%H:%M:%S[.%f]", "%H:%M")
# %z refuses a space before the offset, so the spaced form is a template of its own, and it
# only reads numeric offsets: a named zone needs %Z, which _read turns into UTC
_TIMEZONES = ("%z", " %z", " %Z")


@lru_cache(maxsize=None)
def _with_time(dates: tuple[str, ...], date_time_sep: str, aware: bool) -> tuple[str, ...]:
    return tuple(
        _marked(f"{date}{date_time_sep}{time}{timezone}")
        for date in dates
        for time in _TIME_SUFFIXES
        for timezone in (_TIMEZONES if aware else ("",))
    )


def datetime_templates(val: str, *, aware: bool) -> tuple[str, ...]:
    """Every format the datetime value could plausibly be read with, most preferred first."""
    match = _DATETIME_SPLIT.fullmatch(val)
    if match is None:
        return ()
    date_part = match["date"]
    if not (MIN_LENGTH <= len(date_part) <= MAX_LENGTH):
        return ()
    dates = date_templates(date_part, text_month=False)
    if not dates:
        return ()
    return _with_time(dates, match["t"], aware)


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


def matches_a_template(val: Any, templates_for: Callable[[str], list[str]]) -> bool:
    """Whether some format reads this single value, without settling on which one.

    This is the per-value check the engine runs on every column; unlike infer_column_format it
    stops at the first format that fits, as it has no column to narrow down.
    """
    return isinstance(val, str) and any(parse(val, fmt) is not None for fmt in templates_for(val))


def _templates_for(val: str) -> list[str]:
    if not (MIN_LENGTH <= len(val) <= MAX_LENGTH):
        return []
    return date_templates(val)


def _infer(values: Iterable[Any]) -> str | None:
    return infer_column_format(values, _templates_for)


def _is(val: Any) -> bool:
    return matches_a_template(val, _templates_for)


_test_values = {
    True: [
        "1960-08-07",
        "12/02/2007",
        "12/02/85",
        "15 jan 1985",
        "15 décembre 1985",
        "02 05 2003",
        "20030502",
        "2003.05.02",
        "1/2/2024",
        "15-12-1850",
    ],
    False: [
        "1993-1993-1993",
        "39-10-1993",
        "19-15-1993",
        "15 tambour 1985",
        "12152003",
        "20031512",
        "02052003",
        # a plausible day and month, so only the year window tells this apart from an identifier
        "12341215",
        "6.27367393749392839",
        "1993-12/02",
        "15 jui 1985",
    ],
}
