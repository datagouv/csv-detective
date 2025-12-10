import json

proportion = 1
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


def _is(val) -> bool:
    try:
        j = json.loads(val)
        if isinstance(j, dict):
            if "type" in j and "coordinates" in j:
                return True
            if "geometry" in j and "coordinates" in j["geometry"]:
                return True
    except Exception:
        pass
    return False


_test_values = {
    True: [
        '{"coordinates": [45.783753, 3.049342], "type": "63870"}',
        '{"geometry": {"coordinates": [45.783753, 3.049342]}}',
    ],
    False: ['{"pomme": "fruit", "reponse": 42}'],
}
