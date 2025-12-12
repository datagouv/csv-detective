from csv_detective.formats.longitude_wgs import _is as is_longitude, labels  # noqa

proportion = 1
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"


def _is(val):
    try:
        return is_longitude(val) and -5.5 <= float(val) <= 9.8
    except Exception:
        return False


_test_values = {
    True: ["-2.01", "8.0"],
    False: ["12.8"],
}
