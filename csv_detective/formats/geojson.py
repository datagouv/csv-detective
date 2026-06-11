import json

proportion = 1
description = "JSON object in the [GeoJSON](https://fr.wikipedia.org/wiki/GeoJSON) format"
tags = ["geo"]
python_type = "json"
labels = {
    "json geojson": 1,
    "json": 1,
    "geojson": 1,
    "geo shape": 1,
    "geom": 0.75,
    "geometry": 1,
    "geoshape": 1,
}


def _check_dict(d: dict) -> bool:
    if "type" in d and "coordinates" in d:
        return True
    if "geometry" in d and "coordinates" in d["geometry"]:
        return True
    return False


def _is(val) -> bool:
    if isinstance(val, dict):
        return _check_dict(val)
    try:
        j = json.loads(val)
        if isinstance(j, dict):
            return _check_dict(j)
    except Exception:
        pass
    return False


_test_values = {
    True: [
        '{"coordinates": [45.783753, 3.049342], "type": "63870"}',
        '{"geometry": {"coordinates": [45.783753, 3.049342]}}',
        {"geometry": {"coordinates": [45.783753, 3.049342]}},
        {"coordinates": [45.783753, 3.049342], "type": "63870"},
    ],
    False: ['{"pomme": "fruit", "reponse": 42}'],
}
