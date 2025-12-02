import re
from typing import Any

from csv_detective.formats.date import aaaammjj_pattern, date_casting
from csv_detective.formats.datetime_aware import labels  # noqa

proportion = 1
tags = ["temp", "type"]
threshold = 0.7

# matches AAAA-MM-JJTHH:MM:SS(.dddddd)Z with any of the listed separators for the date OR NO SEPARATOR
pat = (
    aaaammjj_pattern.replace("$", "")
    + r"(T|\s)(0\d|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(.\d{1,6})?$"
)


def _is(val: Any | None) -> bool:
    """Detects naive datetimes only"""
    # early stops, to cut processing time
    # 15 is the minimal length of a datetime format YYMMDDTHH:MM:SS
    # 26 is the maximal length of an ISO datetime format YYYY-MM-DDTHH:MM:SS.dddddd, keeping some slack
    if not isinstance(val, str) or len(val) > 30 or len(val) < 15:
        return False
    # if usual format, no need to parse
    if bool(re.match(pat, val)):
        return True
    if sum([char.isdigit() or char in {"-", "/", ":", " "} for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    return res is not None and not bool(res.tzinfo)


_test_values = {
    True: [
        "2021-06-22 10:20:10",
        "2030/06-22   00:00:00",
        "2030/06/22 00:00:00.0028",
    ],
    False: [
        "2021-06-22T30:20:10",
        "Sun, 06 Nov 1994 08:49:37 GMT",
        "2021-06-44 10:20:10+02:00",
        "1999-12-01T00:00:00Z",
        "2021-06-44",
        "15 décembre 1985",
    ],
}
