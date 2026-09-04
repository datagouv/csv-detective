from typing import Any, Iterable

from csv_detective.formats.date import (
    SHARED_DATE_LABELS,
    datetime_templates,
    infer_column_format,
    matches_a_template,
)

proportion = 1
description = "Datetime with timezone information (flexible formats)"
tags = ["temp", "type"]
python_type = "datetime"
labels = SHARED_DATE_LABELS | {"datetime": 1, "timestamp": 1}

# 16 is the minimal length of a datetime format YYMMDDTHH:MM:SSZ
# 35 is the maximal length of an ISO datetime format YYYY-MM-DDTHH:MM:SS.dddddd+HH:MM, with slack
MIN_LENGTH = 16
MAX_LENGTH = 35


def _templates_for(val: str) -> list[str]:
    if not (MIN_LENGTH <= len(val) <= MAX_LENGTH):
        return []
    return datetime_templates(val, aware=True)


def _infer(values: Iterable[Any]) -> str | None:
    return infer_column_format(values, _templates_for)


def _is(val: Any) -> bool:
    return matches_a_template(val, _templates_for)


_test_values = {
    True: [
        "2021-06-22 10:20:10-04:00",
        "2030-06-22 00:00:00.0028+02:00",
        "2000-12-21 10:20:10.1Z",
        "2024-12-19T10:53:36.428000+00:00",
        "12/31/2022 12:00:00-04:00",
        "1996/06/22 10:20+02:00",
    ],
    False: [
        "2021-06-22T30:20:10",
        "Sun, 06 Nov 1994 08:49:37 GMT",
        "2021-06-44 10:20:10",
        "0.001175692961729795",
        "2030-06-22 00:00:00X0028+02:00",
        "12:00:00-04:00 12/31/2022",
    ],
}
