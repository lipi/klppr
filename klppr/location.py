
from math import sqrt, sin, cos, asin, atan, atan2, radians, degrees


AVG_EARTH_RADIUS_KM = 6371.0


def distance(a, b):
    """
    Return distance in meters between Locations a and b

    >>> distance(Location(0,0), Location(1,0))
    111194.92664455874
    >>> distance(Location(-36,174), Location(-36.02,174.01))
    2398.911028504046
    >>> distance(Location(-36,174), Location(-36.0002,174.0001))
    23.989533843446072
    """
    latlons = [a.lat, a.lon, b.lat, b.lon]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]
    # calculate haversine
    lat = lat2 - lat1
    lon = lon2 - lon1
    alpha = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lon / 2) ** 2
    dist = 2 * AVG_EARTH_RADIUS_KM * 1000 * asin(sqrt(alpha))
    return dist


def bearing(a, b):
    """
    Return bearing in degrees between Locations a and b (from a to b)

    >>> bearing(Location(-36,174), Location(-36.0002,174.0001))
    157.9763041275417
    """
    latlons = [a.lat, a.lon, b.lat, b.lon]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]

    alpha = atan2(sin(lon2-lon1)*cos(lat2),
                  cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1))
    alpha = degrees(alpha)
    alpha = (alpha + 360) % 360
    return alpha


def elevation(a, b):
    """
    Return elevation in degrees between Locations a and b (from a to b)

    >>> elevation(Location(-36,174,0), Location(-36.0002,174.0001,2))
    4.765710402503897
    """
    elev = atan((b.alt - a.alt) / distance(a, b))
    return degrees(elev)


class Location(object):

    """
    Location with geo location in degrees and altitude in meters.
    """

    def __init__(self, lat=None, lon=None, alt=None):
        """
        Location object
        :param lat: latitude in degrees
        :param lon: longitude in degrees
        :param alt: altitude above sea level in meters
        """
        # public fields
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def __repr__(self):
        return str((self.lat, self.lon, self.alt))

