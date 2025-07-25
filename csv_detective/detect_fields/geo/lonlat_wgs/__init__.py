from ..latitude_wgs import _is as is_lat
from ..longitude_wgs import _is as is_lon

PROPORTION = 1


def _is(val):
    """Renvoie True si val peut etre une longitude,latitude"""

    if not isinstance(val, str) or val.count(",") != 1:
        return False
    lon, lat = val.split(",")
    # handling [lon,lat]
    if lon.startswith("[") and lat.endswith("]"):
        lon, lat = lon[1:], lat[:-1]
    return is_lon(lon) and is_lat(lat.replace(" ", ""))
