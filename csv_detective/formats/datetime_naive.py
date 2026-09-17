from typing import Any, Iterable

from csv_detective.formats.date import (
    datetime_templates,
    infer_column_format,
    matches_a_template,
)
from csv_detective.formats.datetime_aware import labels  # noqa

proportion = 1
description = "Datetime with no timezone information (flexible formats)"
tags = ["temp", "type"]
python_type = "datetime"

# 12 is the length of a fully packed datetime, YYYYMMDDHHMM
# 30 is the maximal length of an ISO datetime format YYYY-MM-DDTHH:MM:SS.dddddd, with slack
MIN_LENGTH = 12
MAX_LENGTH = 30


def _templates_for(val: str) -> list[str]:
    if not (MIN_LENGTH <= len(val) <= MAX_LENGTH):
        return []
    return datetime_templates(val, aware=False)


def _infer(values: Iterable[Any]) -> str | None:
    return infer_column_format(values, _templates_for)


def _is(val: Any) -> bool:
    return matches_a_template(val, _templates_for)


_test_values = {
    True: [
        "2021-06-22 10:20:10",
        "2030/06/22 00:00:00.0028",
        "12/31/2022 12:00:00",
        "1996/06/22 10:20",
        "06/12/2022 11:00:15 PM",
    ],
    False: [
        "2021-06-22T30:20:10",
        "06/12/2022 13:00:15 PM",  # a 12-hour clock never goes past 12
        "Sun, 06 Nov 1994 08:49:37 GMT",
        "2021-06-44 10:20:10+02:00",
        "1999-12-01T00:00:00Z",
        "2021-06-44",
        "15 décembre 1985",
        "0.001175692961729795",
        "2030/06-22   00:00:00",
        "12:00:00 12/31/2022",
    ],
}
