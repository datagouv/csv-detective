from decimal import Decimal

from csv_detective.formats.float import _is as is_float

proportion = 1
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


def _is(val):
    try:
        return (
            is_float(val)
            and -90 <= float(val) <= 90
            # we want at (the very) least two decimals
            and Decimal(val).as_tuple().exponent < -1
        )
    except Exception:
        return False


_test_values = {
    True: ["43.2872", "-22.61", "31.00"],
    False: ["100.1973", "40", "-21.2"],
}
