from typing import Any, Optional

from csv_detective.detect_fields.temp.date import date_casting

PROPORTION = 1


def _is(val: Optional[Any]) -> bool:
    """Detects timezone-aware datetimes only"""
    # early stops, to cut processing time
    if not isinstance(val, str) or len(val) > 30 or len(val) < 15:
        return False
    threshold = 0.7
    if sum([char.isdigit() or char in {"-", "/", ":", " "} for char in val]) / len(val) < threshold:
        return False
    res = date_casting(val)
    return (
        res is not None
        and bool(res.hour or res.minute or res.second or res.microsecond)
        and bool(res.tzinfo)
    )
