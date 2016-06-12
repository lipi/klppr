from math import sqrt, sin, cos, asin, atan, atan2, radians, degrees

from klppr.limit import *


'''
Calculations for geodetic locations (latitude,longitude,altitude)
'''


AVG_EARTH_RADIUS_KM = 6371.0


def distance(a, b):
    """
    Return distance in meters between Locations a and b
    """
    if not (a.valid() and b.valid()):
        return 0.0
    latlons = [a.lat, a.lon, b.lat, b.lon]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]
    # calculate Haversine
    lat = lat2 - lat1
    lon = lon2 - lon1
    alpha = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lon / 2) ** 2
    dist = 2 * AVG_EARTH_RADIUS_KM * 1000 * asin(sqrt(alpha))
    return dist


def bearing(a, b):
    """
    Return bearing in degrees between Locations a and b (from a to b)
    """
    if not (a.valid() and b.valid()):
        return 0.0
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
    """
    if not (a.valid() and b.valid()):
        return 0.0
    d = distance(a, b)
    if d == 0:
        return 0.0
    elev = atan((b.alt - a.alt) / d)
    return round(degrees(elev), 3)


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
        # TODO: accuracy
        # TODO: time
        # TODO: (speed, heading, trajectory)

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

    def valid(self):
        """
        :return: True if location is valid
        """
        v = ((self.lat is not None) and
             (self.lon is not None) and
             (self.alt is not None))
        return v

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
