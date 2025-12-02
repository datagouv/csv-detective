import re

from csv_detective.formats.datetime_aware import labels  # noqa

proportion = 1
tags = ["temp", "type"]


def _is(val):
    return isinstance(val, str) and bool(
        re.match(
            r"^[A-Za-z]{3}, (0[1-9]|[1-2][0-9]|3[01]) [A-Za-z]{3} \d{4} "
            r"([0-2])([0-9]):([0-5])([0-9]):([0-5])([0-9]) "
            r"(ut|gmt|est|edt|cst|cdt|mst|mdt|pst|pdt|[+\-](0[0-9]|1[0-3])00)$",
            val.lower(),
            re.IGNORECASE,
        )
    )


_test_values = {
    True: ["Sun, 06 Nov 1994 08:49:37 GMT"],
    False: ["2021-06-22T10:20:10"],
}
