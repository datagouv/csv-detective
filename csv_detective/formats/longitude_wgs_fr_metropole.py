from csv_detective.formats.longitude_wgs import _is as is_longitude, labels  # noqa

proportion = 1
parent = "longitude_wgs"
description = "Longitude within the French metropole bounds in the WGS format"
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"


def _is(val) -> bool:
    try:
        return is_longitude(val) and -5.5 <= float(val) <= 9.8
    except Exception:
        return False


_test_values = {
    True: ["-2.01", "8.0"],
    False: ["12.8"],
}
