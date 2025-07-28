import json

PROPORTION = 0.9


def _is(val):
    """Renvoie True si val peut etre un geojson"""

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
