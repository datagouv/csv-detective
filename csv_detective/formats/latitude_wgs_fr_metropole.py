from csv_detective.formats.latitude_wgs import _is as is_latitude, labels  # noqa

proportion = 1
parent = "latitude_wgs"
description = "Latitude within the French metropole bounds in the WGS format"
tags = ["fr", "geo"]
mandatory_label = True
python_type = "float"


def _is(val) -> bool:
    try:
        return is_latitude(val) and 41.3 <= float(val) <= 51.3
    except Exception:
        return False


_test_values = {
    True: ["42.576", "42.5"],
    False: ["22.5"],
}
