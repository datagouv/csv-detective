from decimal import Decimal

from csv_detective.formats.float import _is as is_float

proportion = 1
tags = ["geo"]
mandatory_label = True
python_type = "float"
SHARED_LONGITUDE_LABELS = {
    "longitude": 1,
    "long": 0.75,
    "lon": 0.75,
    "lng": 0.5,
    "x": 0.5,
    "xf": 0.5,
    "xd": 0.5,
    "coordonnee x": 1,
    "coord x": 1,
    "xcoord": 1,
    "xlon": 1,
    "xlong": 1,
}
labels = SHARED_LONGITUDE_LABELS | {
    "x gps": 1,
    "longitude wgs84": 1,
    "x wgs84": 1,
    "wsg": 0.75,
    "gps": 0.5,
}


def _is(val):
    try:
        return (
            is_float(val)
            and -180 <= float(val) <= 180
            # we want at (the very) least two decimals
            and Decimal(val).as_tuple().exponent < -1
        )
    except Exception:
        return False


_test_values = {
    True: ["120.8263", "-20.27", "31.00"],
    False: ["-200", "20.2"],
}
