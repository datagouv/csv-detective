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
        return is_float(val) and float(val) >= -90 and float(val) <= 90
    except Exception:
        return False


_test_values = {
    True: ["43.2", "-22"],
    False: ["100"],
}
