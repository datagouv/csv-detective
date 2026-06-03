from csv_detective.formats.float import float_casting, _is as is_float
from csv_detective.formats.int import _is as is_int

proportion = 1
description = "Latitude in the WGS format"
tags = ["geo"]
mandatory_label = True
python_type = "float"
SHARED_LATITUDE_LABELS = {
    "latitude": 1,
    "lat": 0.75,
    "y": 0.5,
    "yf": 0.5,
    "yd": 0.5,
    "coordonnee y": 1,
    "coord y": 1,
    "ycoord": 1,
    "ylat": 1,
}
labels = SHARED_LATITUDE_LABELS | {
    "y gps": 1,
    "latitude wgs84": 1,
    "y wgs84": 1,
    "wsg": 0.75,
    "gps": 0.5,
}
INF, SUP = -90, 90


def _is(val: str | float) -> bool:
    if isinstance(val, float):
        return INF <= val <= SUP
    try:
        return (
            is_float(val)
            and INF <= float(val) <= SUP
            # we ideally would like a certain level of decimal precision
            # but 1.200 is saved as 1.2 in csv so we just discriminate ints
            and not is_int(val)
        )
    except Exception:
        return False


_test_values = {
    True: ["43.2872", "-22.61", "-3.0", -3.4],
    False: ["100.1973", "40", 94.5],
}
