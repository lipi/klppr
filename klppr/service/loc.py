from math import sqrt, sin, cos, asin, atan, atan2, radians, degrees

from limit import *

AVG_EARTH_RADIUS_KM = 6371.0


def distance(a, b):
    """
    Return distance in meters between Locations a and b

    >>> distance(Location(0,0), Location(1,0))
    111195.0
    >>> distance(Location(-36,174), Location(-36.02,174.01))
    2399.0
    >>> distance(Location(-36,174), Location(-36.0002,174.0001))
    24.0
    """
    if not (valid(a) and valid(b)):
        return 0.0
    latlons = [a.lat, a.lon, b.lat, b.lon]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]
    # calculate haversine
    lat = lat2 - lat1
    lon = lon2 - lon1
    alpha = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lon / 2) ** 2
    dist = 2 * AVG_EARTH_RADIUS_KM * 1000 * asin(sqrt(alpha))
    return round(dist)


def bearing(a, b):
    """
    Return bearing in degrees between Locations a and b (from a to b)

    >>> bearing(Location(-36,174), Location(-36.0002,174.0001))
    157.976
    >>> # see http://www.gpsvisualizer.com/calculators#distance
    >>> bearing(Location(0, 0), Location(1, 1))
    44.996
    """
    if not (valid(a) and valid(b)):
        return 0.0
    latlons = [a.lat, a.lon, b.lat, b.lon]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]

    alpha = atan2(sin(lon2-lon1)*cos(lat2),
                  cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1))
    alpha = degrees(alpha)
    alpha = (alpha + 360) % 360
    return round(alpha, 3)


def elevation(a, b):
    """
    Return elevation in degrees between Locations a and b (from a to b)

    >>> elevation(Location(-36,174,0), Location(-36.0002,174.0001,2))
    4.764
    """
    if not (valid(a) and valid(b)):
        return 0.0
    d = distance(a, b)
    if d == 0:
        return 0.0
    elev = atan((b.alt - a.alt) / d)
    return round(degrees(elev), 3)


def valid(location):
    """
    :return: True if location is valid

    >>> valid(Location())
    False
    >>> valid(Location(0,0))
    True
    """
    v = ((location.lat != None) and
         (location.lon != None) and
         (location.alt != None))
    return v


class Location(object):

    """
    Location with geo location in degrees and altitude in meters.
    """

    def __init__(self, lat=None, lon=None, alt=0):
        """
        Location object
        :param lat: latitude in degrees
        :param lon: longitude in degrees
        :param alt: altitude above sea level in meters
        """

        # attributes
        self._lat = None
        self._lon = None
        self._alt = 0.0
        # properties
        if lat is not None:
            self.lat = lat
        if lon is not None:
            self.lon = lon
        self.alt = alt

    def __repr__(self):
        return str((self.lat, self.lon, self.alt))

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, x):
        self._lat = limit_tilt(x)

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, x):
        self._lon = limit_pan(x)

    @property
    def alt(self):
        return self._alt

    @alt.setter
    def alt(self, x):
        self._alt = x


if __name__ == "__main__":
    import doctest
    doctest.testmod()