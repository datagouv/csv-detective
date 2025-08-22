import re
from typing import Any, Optional

from csv_detective.detect_fields.temp.date import aaaammjj_pattern, date_casting

PROPORTION = 1
threshold = 0.7

# matches AAAA-MM-JJTHH:MM:SS(.dddddd)±HH:MM with any of the listed separators for the date OR NO SEPARATOR
pat = (
    aaaammjj_pattern.replace("$", "")
    + r"(T|\s)(0\d|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(.\d{1,6})?[+-](0\d|1[0-9]|2[0-3]):([0-5][0-9])$"
)


def _is(val: Optional[Any]) -> bool:
    """Detects timezone-aware datetimes only"""
    # early stops, to cut processing time
    # 21 is the minimal length of a datetime format YYMMDDTHH:MM:SS+HH:MM
    # 32 is the maximal length of an ISO datetime format YYYY-MM-DDTHH:MM:SS.dddddd+HH:MM, keeping some slack
    if not isinstance(val, str) or len(val) > 35 or len(val) < 21:
        return False
    # if usual format, no need to parse
    if bool(re.match(pat, val)):
        return True
    if sum([char.isdigit() or char in {"-", "/", ":", " "} for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    return (
        res is not None
        and bool(res.hour or res.minute or res.second or res.microsecond)
        and bool(res.tzinfo)
    )
