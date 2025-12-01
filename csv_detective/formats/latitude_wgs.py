from csv_detective.formats.float import _is as is_float

proportion = 1
tags = ["geo"]
labels = [
    "latitude",
    "lat",
    "y",
    "yf",
    "yd",
    "coordonnee y",
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
    "latitude wgs84",
    "y wgs84",
    "latitude (wgs84)",
]


def _is(val):
    try:
        return is_float(val) and float(val) >= -90 and float(val) <= 90
    except ValueError:
        return False
    except OverflowError:
        return False


_test_values = {
    True: ["43.2", "-22"],
    False: ["100"],
}
