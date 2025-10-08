import re
from datetime import datetime

from dateparser import parse as date_parser
from dateutil.parser import ParserError
from dateutil.parser import parse as dateutil_parser

PROPORTION = 1
# /!\ this is only for dates, not datetimes which are handled by other utils


def date_casting(val: str) -> datetime | None:
    """For performance reasons, we try first with dateutil and fallback on dateparser"""
    try:
        return dateutil_parser(val)
    except ParserError:
        return date_parser(val)
    except Exception:
        return None


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

threshold = 0.3


def _is(val):
    """Renvoie True si val peut être une date, False sinon"""
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
