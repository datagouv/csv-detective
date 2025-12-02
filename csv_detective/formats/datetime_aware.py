import re

from csv_detective.formats.date import SHARED_DATE_LABELS, aaaammjj_pattern, date_casting

proportion = 1
tags = ["temp", "type"]
labels = SHARED_DATE_LABELS + ["datetime", "timestamp"]

threshold = 0.7
pat = (
    aaaammjj_pattern.replace("$", "")
    + r"(T|\s)(0\d|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(.\d{1,6})"
    + r"?(([+-](0\d|1[0-9]|2[0-3]):([0-5][0-9]))|Z)$"
)


def _is(val):
    # early stops, to cut processing time
    # 16 is the minimal length of a datetime format YYMMDDTHH:MM:SSZ
    # 32 is the maximal length of an ISO datetime format YYYY-MM-DDTHH:MM:SS.dddddd+HH:MM, keeping some slack
    if not isinstance(val, str) or len(val) > 35 or len(val) < 16:
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


_test_values = {
    True: [
        "2021-06-22 10:20:10-04:00",
        "2030-06-22 00:00:00.0028+02:00",
        "2000-12-21 10:20:10.1Z",
        "2024-12-19T10:53:36.428000+00:00",
        "1996/06/22 10:20:10 GMT",
    ],
    False: ["2021-06-22T30:20:10", "Sun, 06 Nov 1994 08:49:37 GMT", "2021-06-44 10:20:10"],
}
