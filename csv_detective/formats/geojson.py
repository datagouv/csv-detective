import json

proportion = 1
tags = ["geo"]
labels = [
    "json geojson",
    "json",
    "geojson",
    "geo shape",
    "geom",
    "geometry",
    "geo shape",
    "geoshape",
]


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
