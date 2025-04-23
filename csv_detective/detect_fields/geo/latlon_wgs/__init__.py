from ..latitude_wgs import _is as is_lat
from ..longitude_wgs import _is as is_lon

PROPORTION = 1


def _is(val):
    '''Renvoie True si val peut etre une latitude,longitude'''

    if not isinstance(val, str) or val.count(",") != 1:
        return False
    lat, lon = val.split(",")
    return is_lat(lat) and is_lon(lon.replace(" ", ""))
