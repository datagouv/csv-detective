from csv_detective.formats.float import _is as is_float
from csv_detective.formats.int import _is as is_int

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
            # we ideally would like a certain level of decimal precision
            # but 1.200 is saved as 1.2 in csv so we just discriminate ints
            and not is_int(val)
        )
    except Exception:
        return False


_test_values = {
    True: ["120.8263", "-20.27", "31.0"],
    False: ["-200", "20"],
}
