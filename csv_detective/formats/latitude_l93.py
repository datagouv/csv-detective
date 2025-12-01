from frformat import LatitudeL93

from csv_detective.formats.float import _is as is_float
from csv_detective.formats.float import float_casting

proportion = 1
tags = ["fr", "geo"]
labels = [
    "latitude",
    "lat",
    "y",
    "yf",
    "yd",
    "y l93",
    "coordonnee y",
    "latitude lb93",
    "coord y",
    "ycoord",
    "geocodage y gps",
    "location latitude",
    "ylatitude",
    "ylat",
    "latitude (y)",
    "latitudeorg",
    "coordinates.latitude",
    "googlemap latitude",
    "latitudelieu",
    "latitude googlemap",
]

_latitudel93 = LatitudeL93()


def _is(val):
    try:
        if isinstance(val, str) and is_float(val):
            return _latitudel93.is_valid(float_casting(val))

        return False

    except (ValueError, OverflowError):
        return False


_test_values = {
    True: ["6037008", "7123528.5", "7124528,5"],
    False: ["0", "-6734529.6", "7245669.8", "3422674,78", "32_34"],
}
