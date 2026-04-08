import re

from csv_detective.formats.datetime_aware import labels  # noqa

proportion = 1
description = "Datetime in the RFC822 format"
tags = ["temp", "type"]
python_type = "datetime"


def _is(val) -> bool:
    return isinstance(val, str) and bool(
        re.match(
            r"^(mon|tue|wed|thu|fri|sat|sun), (0[1-9]|[1-2][0-9]|3[01]) "
            r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) \d{4} "
            r"([01][0-9]|2[0-3]):([0-5])([0-9]):([0-5])([0-9]) "
            r"(ut|gmt|est|edt|cst|cdt|mst|mdt|pst|pdt|[+\-](0[0-9]|1[0-3])00)$",
            val.lower(),
            re.IGNORECASE,
        )
    )


_test_values = {
    True: ["Sun, 06 Nov 1994 08:49:37 GMT", "Mon, 24 Feb 2010 23:00:37 +1000"],
    False: [
        "2021-06-22T10:20:10",
        "Sun, 06 Nov 1994 25:49:37 GMT",
        "Lun, 06 Nov 1994 08:49:37 GMT",
    ],
}
